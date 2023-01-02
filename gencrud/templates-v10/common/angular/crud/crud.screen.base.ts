import { FormGroup, FormControl } from '@angular/forms';
import { OnInit, Input, OnDestroy, Component, Injectable } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { GcCrudServiceBase } from './crud.service.base';
import { GcSubscribers } from '../subscribers';
import { isNullOrUndefined } from 'util';
import Swal from 'sweetalert2';
import { Subject } from 'rxjs';

export class ActionEvent<T>
{
    public Record: T;
    public Status: boolean;
    public Data: any;

    constructor( status: boolean, record: T = null, data: any = null )
    {
        this.Status = status;
        this.Record = record;
        this.Data = data;
    }
};

// @Component( {
// 	template: ''
// } )
@Injectable()
// tslint:disable-next-line:component-class-suffix
export class GcScreenBase<T> extends GcSubscribers implements OnInit, OnDestroy
{
	@Input()	id: string;
	@Input()	value: any;
	@Input()	mode: string;	// edit, add, filter
    public      saveButtonClicked: Subject<boolean> = new Subject();
    private     callBack: ( event: ActionEvent<T> ) => any;
    public      callBackData: any = null;
	public      row: T;
	public      formGroup: FormGroup;
	public      formControl: FormControl;
	public      sub: any;
	protected   fixedValues: any = null;
    protected   debug: boolean = false;
    public      tabIndex: number = 0;

	constructor( protected name: string,
                 protected route: ActivatedRoute,
                 public dataService: GcCrudServiceBase<T>
                )
	{
		super();
		return;
	}

	protected updateFormGroup( record: T ): void
	{
		return;
	}

	public ngOnInit(): void 
    {
        if ( this.id === undefined || this.id === null )
        {
            this.registerSubscription( this.route.queryParams.subscribe( params => {
                this.id             = params.id;    // Contains the key field, currently only the primary key is supported.
                this.value          = params.value; // Contains val value for the key field.
                this.mode           = params.mode;  // edit or new, filter only supported on the table component.
                this.updateFixedValues( params );
            } ) );
        }
        if ( this.value != null || this.value !== undefined )
        {
            this.registerSubscription( this.dataService.getRecordById( this.value ).subscribe( record => {
				this.row = record;
                console.log("***************************", record)
				this.updateFormGroup( this.row );
                this.updateFixedValues();
                this.dataService.lockRecord( this.row );
            } ) );
        }
        this.restoreView();
        return;
    }
    
    public onTabChanged( $event ): void 
    {
        console.log( 'onTabChanged', $event );
        this.tabIndex = $event.index;
        this.storeView();
    }

	public ngOnDestroy(): void 
    {
		this.dataService.unlockRecord( this.row );
        this.storeView();
        super.ngOnDestroy();
        return;
    }

    public doInitialize(id, value, callback: ( event: ActionEvent<T> ) => any, data: any): void {
        this.id = id;
        this.value = value;
        this.mode = 'edit';
        this.callBack = callback;
        this.callBackData = data;
        this.ngOnInit();
    }

	protected updateFixedValues( fixed_values: any = null ): void
    {
        if ( fixed_values != null )
        {
            this.fixedValues = fixed_values;
        }
        if ( this.fixedValues != null )
        {
            for ( const key in this.fixedValues )
            {
                if ( key.endsWith( '_ID' ) )
                {
                    console.log("id-key")
                    const value: number = +this.fixedValues[ key ];
                    const ctrl = this.formGroup.get( key );
                    if ( ctrl != null )
                    {
                        ctrl.setValue( value );
                        if ( !this.editMode )
                        {
                            ctrl.disable( { onlySelf: true } );
                        }
                    }
                }
            }
        }
        return;
    }

	public get editMode(): boolean
    {
        return ( this.mode === 'edit' );
	}

	public onCancelClick(): void 
	{
        this.dataService.unlockRecord( this.row );
        if ( isNullOrUndefined( this.callBack ) )
        {
            window.history.back();
        }
        else
        {
            this.callBack( new ActionEvent<T>( false ) );
        }
        return;		
	}
	
	public onSaveClick(): void 
	{
        // tell child components that the save button was clicked 
        this.saveButtonClicked.next(true);
        // proceed with default saving behavior
		if ( !this.editMode )
        {
            if ( this.fixedValues != null )
            {
                for ( const key in this.fixedValues )
                {
                    if ( key.endsWith( '_ID' ) )
                    {
                        const value: number = +this.fixedValues[ key ];
                        const ctrl = this.formGroup.get( key );
                        if ( ctrl != null )
                        {
                            ctrl.enable( { onlySelf: true } );
                            ctrl.setValue( value );
                        }
                    }
                }
            }
            Swal.fire('Creating new entry')
            Swal.showLoading();
            this.registerSubscription(
                this.dataService.addRecord( this.formGroup.value ).subscribe( record => {
                    this.registerSubscription(this.dataService.getPrimaryKey().subscribe(result => {
                        const id = result["primaryKey"];
                        this.id = id;
                        this.value = record[id];
                        this.mode = "edit";
                        this.ngOnInit();

                        Swal.fire({
                            position: 'bottom-end',
                            icon: 'success',
                            title: 'New item successfully created',
                            showConfirmButton: false,
                            timer: 1500
                        });
                    }))}, error => {
                        Swal.fire({
                            position: 'bottom-end',
                            icon: 'error',
                            title: 'Something went wrong. Please try again or contact the developers.',
                            html: error.message,
                            showConfirmButton: true
                        });
                    }
                )
            );
        }
        else
        {
            Swal.fire('Saving changes...')
            Swal.showLoading();
            this.registerSubscription(
                this.dataService.updateRecord( this.formGroup.value ).subscribe( record => {
                    Swal.fire({
                        position: 'bottom-end',
                        icon: 'success',
                        title: 'Changes successfully saved',
                        showConfirmButton: false,
                        timer: 1500
                    });
                }, error => {
                    Swal.fire({
                        position: 'bottom-end',
                        icon: 'error',
                        title: 'Something went wrong. Please try again or contact the developers.',
                        html: error.message,
                        showConfirmButton: true
                    });
                })
            );
		}

        // unlocking disabled because saving does not close the component
        // this.dataService.unlockRecord( this.row );
        if ( isNullOrUndefined( this.callBack ) )
        {
            // window.history.back();
        }
        else
        {
            this.callBack( new ActionEvent<T>( true, this.formGroup.value, this.callBackData ) );
        }
		return;
	}

    private storeView(): void
    {
        if(!isNullOrUndefined(this.id)) {
		    sessionStorage.setItem( "tab-" + this.id.toString(), JSON.stringify( this.tabIndex ) );
        }
        return;
    }

    private restoreView(): void
    {
        if(!isNullOrUndefined(this.id)) {
            const data = sessionStorage.getItem( "tab-" + this.id.toString() );
            if ( !isNullOrUndefined( data ) )
            {
                this.tabIndex = JSON.parse( data );
            }
        }
        return;
    }
}
