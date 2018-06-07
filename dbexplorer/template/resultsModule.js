/**
 * Class managing results.
 */
class ResultsModule {
	/**
	 * Create result module
	 * @param {Controls} controls
	 * @param {Data} data
	 */
	constructor(controls, data) {
		this.controls = controls;
		this.data = data;
	}
	
	/**
	 * Create and displaye all tables
	 * @param {Array<object>} tables - tables as json objects
	 */
	showTables(tables) {
		this.controls.output.results.empty();
		if (tables.length > 0) {
			tables.forEach(table => this.addTable(table));
		} else {
			this.controls.output.results.append("No matching tables");
		}
	}
	
	/**
	 * Convert table from json data to html
	 * @param {object} table - table as json object
	 */
	addTable(table) {
		var table = new Table(table, this.controls);
		this.controls.output.results.append(table.content);
	}
}