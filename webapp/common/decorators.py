import functools
from flask import request, Response, jsonify
from pydantic import BaseModel, ValidationError
import webapp.api as API
from typing import List, Optional, Any, Union
from flask import Response, abort
from pydantic import BaseModel, ValidationError
from webapp.common.util import Right



def no_pre_processing(blueprint: str = None):
    """
    Decorate a function with the instruction to dont apply flask before_request handler

    Parameters
    ----------
    blueprint : str, optional
        The name of the api blueprint object
    """
    def decorator(function):
        key = blueprint + "." + function.__name__ \
            if blueprint is not None else function.__name__

        API.no_pre_processing[key] = function
        return function
    return decorator


def requires_access(blueprint: str = None, rights: list = []):
    """
    Decorate a function with the list of access rights it requires

    Parameters
    ----------
    blueprint : str, optional
        The name of the api blueprint object
    rights : List[Right], optional
        The list of required access rights
    """
    def decorator(function):
        key = function.__name__
        if blueprint is not None:
            key = blueprint + "." + function.__name__
    
        API.required_rights[key] = set(rights) if len(rights) > 0 or rights != [Right.ALL] \
                else set([Right.CREATE, Right.DELETE, Right.READ, Right.UPDATE])
        return function
    return decorator

class ErrorDescription (BaseModel):
    code: int
    message: str
    category: str
    details: Optional[Any] # Schema depends on category.


def list_to_jsonpath ( parts: List[Union[str,int]] ) -> str :
    """
    Converts a list of parts into a simplified JSON Path expression.
    Example:  ('processes',2,'flag')  -->  "$['processes'][2]['flag']"
    """
    fullpath = "$"
    for p in parts:
        if type(p) == str :
            fullpath += "['" + p + "']"
        else :
            fullpath += "[" + str(p) + "]"
    return fullpath


def build_error (
    status_code:int, problem:str, solution:str, category:str, details:Optional[Any]=None
) :
    """
    Build a generic error that is not specialized for any case.
    """
    error_desc = ErrorDescription(
        code=status_code,
        message=( problem + " " + solution ),
        category=category,
        details=details
    )
    return Response(
        response=error_desc.json(by_alias=False),
        status=status_code,
        mimetype='application/json'
    )

def abort_with_input_error ( validation_error:ValidationError ) :
    """
    Validation errors that reference invalid input delivered to endpoints.
    """
    problem = "Invalid input structure was sent to the endpoint."
    solution = "Compare input with accepted JSON-Schemas."
    errorResponse = build_error(
        status_code=400, problem=problem, solution=solution, category="input",
        details=[
            "{} : {} ({})".format( list_to_jsonpath(entry["loc"]), entry["msg"], entry["type"] )
            for entry in validation_error.errors()
        ]
    )
    return abort(errorResponse)


def abort_with_output_error ( validation_error:ValidationError ) :
    """
    Validation errors that reference invalid output delivered from the endpoints.
    """
    problem = "Invalid output structure was sent from the endpoint."
    solution = "Notify the backend developers."
    errorResponse = build_error(
        status_code=401, problem=problem, solution=solution, category="output",
        details=[
            "{} : {} ({})".format( list_to_jsonpath(entry["loc"]), entry["msg"], entry["type"] )
            for entry in validation_error.errors()
        ]
    )
    return abort(errorResponse)


def abort_with_error ( error: Exception, problem: str, solution: str, status_code: int = 500 ) :
    """
    General errors
    """
    errorResponse = build_error(
        status_code=status_code, problem=problem, solution=solution, category="server",
        details=[str(error)]
    )
    return abort(errorResponse)



def with_valid_input ( params=None, body=None ):
    """
    Decorate a function with a pydantic input validation on the decorated function's first
    argument, which has to match the decorator argument.

    Parameters
    ----------
    params : SpecificClass<pydantic.BaseModel>, optional
        The class of the pydantic model that will validate the query params and pass it along.
    body : SpecificClass<pydantic.BaseModel>, optional
        The class of the pydantic model that will validate the json body and pass it along.

    Execution Flow
    --------------
    Adds argument `params` : SpecificInstance<pydantic.BaseModel>
    Adds argument `body` : SpecificInstance<pydantic.BaseModel>
    """

    def decorator(func):

        @functools.wraps(func)
        def decorated_function(*args, **kwargs):

            # Retrieve and validate whatever inputs where supplied.
            try:
                if request.is_json:
                    input_body = request.get_json()
                    body_model = body.parse_obj(input_body)
                    kwargs['body'] = body_model  # Passed as keyword argument.

                elif request.form is not None:
                    input_body = {**request.form.to_dict(), **request.files.to_dict()}
                    body_model = body.parse_obj(input_body)
                    kwargs['body'] = body_model  # Passed as keyword argument.

                else:
                    # Retrieve and validate the query params if they were specified.
                    if params is not None:
                        input_params = request.args.to_dict()
                        params_model = params.parse_obj(input_params)
                        kwargs['params'] = params_model  # Passed as keyword argument.

            # Validation errors may occur in any of the inputs.
            # TODO: This could be made more specific by telling whether params or body has failed.
            except ValidationError as e:
                print("error:", e)
                return abort_with_input_error( validation_error=e )

            except Exception as e:
                print(e)
                return e

            return func(*args, **kwargs)

        # Add information to the function about the schemas that have been used.
        #if params is not None :
        #    decorated_function.input_params = params
        #if body is not None :
        #    decorated_function.input_body = body

        return decorated_function

    return decorator


def with_valid_output ( output, format:bool=True ) :
    """
    Decorate a function with a pydantic output validation on the decorated function's return.

    Parameters
    ----------
    output : SpecificClass<pydantic.BaseModel>
        The class of the pydantic model that will validate the response.
    format : bool
        True if the output should be formatted. This will likely transform properties into camelCase.

    Returns
    -------
    function(*args, **kwargs)
        Decorated function where the return value will be validated.

    Influences
    ----------
    Configuration.assert_valid_output
        This method is disabled if the configuration is false.
    """

    def decorator(func):

        @functools.wraps(func)
        def decorated_function(*args, **kwargs):
            func_return = func(*args, **kwargs)

            # Output of a Flask View might be the response or a tuple with ( response, ... )
            # @todo It might be something else as well as described in
            #   https://flask.palletsprojects.com/en/1.1.x/quickstart/#about-responses
            #   but this decorator will only attempt to identify two of the cases.
            func_output = None
            modifyResponse = False
            if type(func_return) == dict:
                func_output = func_return
                modifyResponse = True
            # response is of type output
            elif type(func_return) == output:
                formatted_output = func_return
                modifyResponse = True
            elif type(func_return) == tuple:
                func_output = func_return[0]
                modifyResponse = True
            elif type(func_return) == Response:
                func_output = func_return.json
            else:
                # @todo : Error message is lacking information to pinpoint the problem.
                API.logger.warn("Output validation could not identify returned value: " + str(type(func_return)) )
                return func_return

            # dont validate the response value it if it was already a correct output object
            if type(func_return) != output:
                # If the return value was identified, then validate it and abort if invalid.
                formatted_output = None
                try:
                    formatted_output = output.parse_obj(func_output) # No return on purpose, only validate and discard.
                except ValidationError as e:
                    return abort_with_output_error( validation_error=e )

            if modifyResponse:
                # jsonify output
                return jsonify(formatted_output.dict(by_alias=format)) # Convert output to camelCase style.
            else:
                # Pass the original return.
                return func_return

        # Add information to the function about the schemas that have been used.
        #if output is not None:
        #    decorated_function.output_body = output

        return decorated_function

    return decorator
