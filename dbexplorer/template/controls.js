/**
 * Intermediate class between html and js. Contains all html controls for input and output.
 * @property {object}  input - html controls used for data input
 * @property {object}  input.searchValue - html input control for search value
 * @property {object}  input.searchType - html select control for search type (table, column or value)
 * @property {object}  input.matchingColumns - html checkbox control indicating whether to display mismatched columns
 * @property {object}  input.matchingColumnsContainer - container of input.matchingColumns
 * @property {object}  output - html controls used for data output
 * @property {object}  output.databaseName - html div for displaying db name
 * @property {object}  output.databaseName - html div for displaying report results
 */
class Controls {
	/**
	 * Gets control from html using jquery.
	 */
	constructor() {
		this.input = {
			
			searchValue: $('#input-search-value'),
			searchType: $('#input-search-type'),
			matchingColumns: $('#input-matching-columns'),
			matchingColumnsContainer: $('#input-container-matching-columns')
		}
		
		this.output = {
			databaseName: $('#output-database-name'),
			results: $('#output-results')
		}
	}
}