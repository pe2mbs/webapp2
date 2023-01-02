import { Component, Input, OnInit } from '@angular/core';

@Component({
    selector: 'app-row-extra-button',
    template: `
    <ng-container [ngSwitch]="directive">
        <app-compare-files-button
        *ngSwitchCase="'app-compare-files-button'"
        [cssClass]="cssClass"
        [id]="attributes.id"
        [value]="attributes.value"
        [record]="record"
        [tooltip]="attributes.tooltip">
        </app-compare-files-button>

        <app-jira-button
        *ngSwitchCase="'app-jira-button'"
        [cssClass]="cssClass"
        [id]="attributes.id"
        [value]="attributes.value"
        [name]="attributes.name"
        [issueID]="attributes.issueID"
        [tooltip]="attributes.tooltip">
        </app-jira-button>
    </ng-container>
    `,
    styles: [ '' ]
})
export class RowExtraButtonsComponent
{
    @Input( 'directive' )           directive: string;
    @Input( 'attributes' )          attributes: any = {};
    @Input( 'record' )              record: any = {};
    @Input( 'cssClass' )            cssClass: string;

    constructor() {}

}
