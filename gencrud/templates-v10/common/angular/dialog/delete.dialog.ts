/*
#
#   Python backend and Angular frontend code generation by gencrud
#   Copyright (C) 2018-2020 Marc Bertens-Nguyen m.bertens@pe2mbs.nl
#
#   This library is free software; you can redistribute it and/or modify
#   it under the terms of the GNU Library General Public License GPL-2.0-only
#   as published by the Free Software Foundation.
#
#   This library is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#   Library General Public License for more details.
#
#   You should have received a copy of the GNU Library General Public
#   License GPL-2.0-only along with this library; if not, write to the
#   Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#   Boston, MA 02110-1301 USA
#
#   gencrud: 2020-12-18 21:35:19 version 2.1.657 by user mbertens
*/
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { Component, Inject } from '@angular/core';
import { GcBaseDialog } from './dialog';


@Component({
    // tslint:disable-next-line:component-selector
    selector: 'gc-delete-dialog',
    templateUrl: './delete.dialog.html',
    styleUrls: ['./dialog.scss']
})
// tslint:disable-next-line:component-class-suffix
export class GcDeleteDialog extends GcBaseDialog
{
    constructor( dialogRef: MatDialogRef<GcDeleteDialog>,
                 @Inject( MAT_DIALOG_DATA ) public data: any )
    { 
		super( dialogRef, data.service );
        return;
    }

    public onSaveClick(): void
    {
        this.data.service.deleteRecord( this.data.record[ this.data.id ] );
        return;
    }
}

