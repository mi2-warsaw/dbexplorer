/**
 * The class of all data needed to generate report. Data is generated as json in Python. Contains method for clearing empty tables.
 */
class Data {
	constructor() {
		return this.modifyTables({{data}});
	}
	
	/**
	 * Delete unnecessary data from columns on empty tables. It leaves the name of the column and the SQL type. Changes 'distinct' column to empty string if is null
	 * @param {Data} data - raport data in json.
	 * @return {Data} Cleared data.
	 */
	modifyTables(data) {
		data.tables.forEach(table => {
			table.columns.forEach(column => {
				if(table.records == 0) {
					column.data = column.data.filter(data => data.key === 'Name' || data.key == 'SQL Type')
				}
				column.data.forEach(data => {
					if (data.key === 'Distinct' && data.value === null) {
						data.value = '';
					}
				})
			});
		});
		return data;
	}
}