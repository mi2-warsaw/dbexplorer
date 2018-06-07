/**
 * The class of all data needed to generate report. Data is generated as json in Python. Contains method for clearing empty tables.
 */
class Data {
	constructor() {
		return this.clearEmptyTables({{data}});
	}
	
	/**
	 * Delete unnecessary data from columns on empty tables. It leaves the name of the column and the SQL type
	 * @param {Data} data - raport data in json.
	 * @return {Data} Cleared data.
	 */
	clearEmptyTables(data) {
		data.tables.forEach(table => {
			if(table.records == 0) {
				table.columns.forEach(column => {
					column.data = column.data.filter(data => data.key === 'Name' || data.key == 'SQL Type')
				});
			}
		});
		return data;
	}
}