import functools
from flask import request, Response, jsonify
from pydantic import BaseModel, ValidationError
import webapp2.api as API
from webapp2.common.error import *



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