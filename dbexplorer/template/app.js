/**
 * Initializing application. Run on load.
 */
$(function() {
	data = new Data();
	controls = new Controls();
	controls.output.databaseName.append(`${data.database}`);
	
	resultsModule = new ResultsModule(controls, data);
	searchModule = new SearchModule(controls, data, resultsModule);
	resultsModule.showTables(data.tables);
})