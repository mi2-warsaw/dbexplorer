/**
 * Class managing table search.
 */
class SearchModule {
	/**
	 * Create search module
	 * @param {Controls} controls
	 * @param {Data} data
	 * @param {ResultsModule} results
	 */
	constructor(controls, data, results) {
		this.controls = controls;
		this.data = data;
		this.results = results;
		this.controls.input.searchValue.on('input', () => this.search());
		this.controls.input.searchType.on('input', () => this.search());
		this.controls.input.matchingColumns.on('change', () => this.search());
	}
		
	/**
	 * Gets search type and value and initialize searching
	 */
	search() {
		var type = this.controls.input.searchType.val();
		var value = this.controls.input.searchValue.val();
		if (type != 'column') {
			this.controls.input.matchingColumnsContainer.hide();
		} else {
			this.controls.input.matchingColumnsContainer.show();
		}
		this.filter(type, value);
	}
	
	/**
	 * Searches the tables according to the specified type and value. Initialize displaying filtered tables
	 * @param {string} type - search type (table, column or value)
	 * @param {string} value - search value
	 */
	filter(type, value) {
		var filteredTables = data.tables;
		if (value.length != 0) {
			value = value.toLowerCase();
			switch (type) {
				case 'table':
					filteredTables = this.filterByTables(value);
					break;
				case 'column':
					filteredTables = this.filterByColumn(value);
					break;
				case 'value':
					filteredTables = this.filterByValue(value);
					break;
			}
		}
		this.results.showTables(filteredTables);
	}

	/**
	 * Filters tables by specified table name
	 * @param {string} value - search value
	 * @return {Array<object>} - filtered by value tables as json data
	 */
	filterByTables(value) {
		return this.data.tables.filter(table => {
			return table.name.toLowerCase().indexOf(value) >= 0;
		});
	}

	/**
	 * Filters tables by specified column name
	 * @param {string} value - search value
	 * @return {Array<object>} - filtered by value tables as json data
	 */
	filterByColumn(value) {
		return this.data.tables.filter(table => {
			return table.columns.some(column => {
				return this.getColumnName(column).toLowerCase().indexOf(value) >= 0;
			});
		});
	}

	/**
	 * Filters tables by specified value
	 * @param {string} value - search value
	 * @return {Array<object>} - filtered by value tables as json data
	 */
	filterByValue(value) {
		return this.data.tables.filter(table => {
			return table.columns.some(column => {
				return column.data.some(data => {
					return data.value.toString().toLowerCase().indexOf(value) >= 0;
				});
			});
		});
	}

	/**
	 * Gets (creates if non existing) column name
	 * @param {object} column - column as json data
	 * @return {string} - column name
	 */
	getColumnName(column) {
		if (!column.name) {
			column.name = column.data.find(data => data.key == 'Name').value;
		}
		return column.name;
		 
	}
	
}