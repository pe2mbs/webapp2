export interface GcMenuItem
{
	displayName: string;
	iconName: string;
	route?: string;
	id: string;
	disabled?: boolean;
	childeren?: GcMenuItem[];
}
