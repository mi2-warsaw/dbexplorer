/**
 * Class for converting table from json to html
 * @property {object} content - table as html
 */
class Table {
	/**
	 * Creates table
	 * @param {object} table - table as json data
	 * @param {Controls} controls
	 */
	constructor(table, controls) {
		this.controls = controls;
		
		var header = this.createHeader(table);
		var body = this.createBody(table.columns);

		var collapseWrapper = this.createCollapseWrapper(table.name);
		collapseWrapper.append(body);

		this.content = this.createCard(header, collapseWrapper);
	}
	
	/**
	 * Combines together header and body of table
	 * @param {object} header - table header, collapsable div
	 * @param {object} body - table body, html tables with report
	 */
	createCard(header, body) {
		var card = $('<div class="card"></div>');
		card.append(header, body);
		return card;
	}
	
	/**
	 * Creates table header - collapsable div
	 * @param {object} table - table as json data
	 * @returns {object} table header - collapsable div
	 */
	createHeader(table) {
		return `<div class="card-header" id="headingOne"> 
					<h5 class="mb-0"> 
						<button class="btn btn-link collapsed" data-toggle="collapse" data-target="#collapse${table.name}" aria-expanded="true" aria-controls="collapse${table.name}"> 
							${table.name} (columns: ${table.columns.length}, records: ${table.records})
						</button> 
					</h5> 
				</div>`;
	}
	
	/**
	 * Creates table body - html tables (column sorted by type) with report data
	 * @param {Array<object>} columns - table columns as json data
	 * @returns {object} table body - html table with report data
	 */
	createBody(columns) {
		var cardBody = $(`<div class="card-body"></div>`);
		
		var numericColumns = columns.filter((column) => column.type === 'numeric');
		var characterColumns = columns.filter((column) => column.type === 'character');
		var dateColumns = columns.filter((column) => column.type === 'datetime');
		var otherColumns = columns.filter((column) => ['numeric', 'character', 'datetime'].indexOf(column.type) < 0 );

		cardBody.append(this.createColumns(numericColumns, 'Numeric columns'),
			this.createColumns(characterColumns, 'Character columns'),
			this.createColumns(dateColumns, 'Datetime columns'),
			this.createColumns(otherColumns, 'Other columns'))

		return cardBody;
	}
	
	/**
	 * Creates report for columns of specific type (numeric, character, date or other)
	 * @param {Array<object>} columns - table columns of specific type as json data
	 * @param {string} header - header for table with typed columns report
	 * @returns {object} table body - html div with report
	 */
	createColumns(columns, header) {
		if(columns.length == 0) {
			return;
		}
		var notEmpty = false;
		
		var thead = this.createColumnTableHeader(columns[0]);
		var tbody = $('<tbody></tbody>');
				
		columns.forEach(column => {
			if(this.showColumn(column)) {
				tbody.append(this.createColumnRow(column));
				notEmpty = true;
			}
		})
		
		if(!notEmpty) {
			return;
		}
		
		var table = $('<table class="table table-stripped"></table>').append(thead, tbody);
		var header = $(`<h5 class="normal-text">${header}</h5>`);
		return $('<div class="column-table"></div>').append(header, table);
	}
	
	/**
	 * Creates data header for columns table report
	 * @param {object} column - any column (as json data) of specific type
	 * @returns {object} thead with data headers
	 */
	createColumnTableHeader(column) {
		var row = $('<tr></tr>');
		column.data.forEach(function (data) {
			row.append(`<th>${data.key}</th>`);
		});
		return $('<thead></thead>').append(row);
	}
	
	/**
	 * Checks whether the column should be shown
	 * @param {object} column - column as json data
	 * @returns {boolean} if the column should be shown
	 */
	showColumn(column) {
		var showOnlyMatching = this.controls.input.searchType.val() === "column" && this.controls.input.matchingColumns.is(':checked');
		return !showOnlyMatching || this.getColumnName(column).toLowerCase().indexOf(controls.input.searchValue.val()) >= 0;
	}
	
	/**
	 * Creates report table row for column
	 * @param {object} column - column as json data
	 * @returns {object} html row with column data
	 */
	createColumnRow(column) {
		var row = $('<tr></tr>');
		column.data.forEach(data => {
			var value = data.value instanceof Array ? data.value.map(this.nullToString).join('</br>') : this.nullToString(data.value);
			row.append(`<td>${value}</td>`);
		});
		return row;
	}
	
	/**
	 * Collapsable wrapper for table report body
	 * @param {string} tableName - table name
	 * @returns {object} html div which is a wrapper for report body
	 */
	createCollapseWrapper(tableName) {
		return $(`<div id="collapse${tableName}" class="collapse" aria-labelledby="heading${tableName}" data-parent="#output-results"></div>`);
	}
	
	/**
	 * Helper method. Change null to string 'null'
	 * @param {object} value
	 * @returns {object} string 'null' if value is null, value otherwise
	 */
	nullToString(value) {
		return value == null ? "null" : value;
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