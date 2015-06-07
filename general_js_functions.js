// functions for sorting tables

function setTableRowAltClass(tableId) {
	var t = document.getElementById(tableId);
	var tBody = t.getElementsByTagName('tbody')[0];
	var j = false;
	for (var i = 0, row; row =tBody.rows[i]; i++) {
		if (row.style.display != "none") {
			if ( j == true ) {
				row.className = "alt";
				j = false;
				}
			else {
				row.className = "";
				j = true;
				}
			}
		}
	}

function makeObjectMapFromTableHeader(tableId) {
	var t = document.getElementById(tableId);
	var tHead = t.getElementsByTagName('thead')[0];
	var retArray = [];
	for (i = 0; cell = tHead.rows[0].cells[i];i++) {
		retArray.push(cell.innerHTML);
		}
	return retArray;
	}

function makeArrayFromTable(tableId) {
	var t = document.getElementById(tableId);
	var tBody = t.getElementsByTagName('tbody')[0];
	var tableMap = makeObjectMapFromTableHeader(tableId);
	var retArray = [], temp;
	for (var i = 0, row; row =tBody.rows[i]; i++) {
		temp = {};
		temp['display'] = row.style.display;
		for (var j = 0, cell; cell = row.cells[j]; j++) {
			temp[tableMap[j]] = cell.innerHTML;
			temp[tableMap[j]+'Text'] = cell.textContent;
			}
		retArray.push(temp);
		}
	return retArray;
	}

function makeTableFromArray(tableId,sourceArray) {
	var t = document.getElementById(tableId);
	var tBody = t.getElementsByTagName('tbody')[0], r, c;
	var tableMap = makeObjectMapFromTableHeader(tableId);
	for (var i = 0, row; row = tBody.rows[i]; i=i) {
		tBody.deleteRow(i);
		}
	for (i = 0; i < sourceArray.length; i++) {
		r = tBody.insertRow(i);
		for (var j = 0; j < tableMap.length; j++) {
			c = r.insertCell(j);
			c.innerHTML = sourceArray[i][tableMap[j]];
			}
		r.style.display = sourceArray[i]['display'];
		}
	}
	
function compareRows(sortType,sortOrder) {
	return function(a,b) {
		if (((a[sortType+'Text'].toUpperCase() > b[sortType+'Text'].toUpperCase()) && (sortOrder == 'Ascending')) || ((a[sortType+'Text'] < b[sortType+'Text']) && (sortOrder == 'Descending')))
			return 1;
		else if (((a[sortType+'Text'].toUpperCase() < b[sortType+'Text'].toUpperCase()) && (sortOrder == 'Ascending')) || ((a[sortType+'Text'].toUpperCase() > b[sortType+'Text'].toUpperCase()) && (sortOrder == 'Descending')))
			return -1;
		else return 0;
		}
	}

function compareDateRows(sortType,sortOrder) {
	return function(a,b) {
		aDate = new Date(a[sortType+'Text']);
		bDate = new Date(b[sortType+'Text']);
		if (((aDate > bDate) && (sortOrder == 'Ascending')) || ((aDate < bDate) && (sortOrder == 'Descending')))
			return 1;
		else if (((aDate < bDate) && (sortOrder == 'Ascending')) || ((aDate > bDate) && (sortOrder == 'Descending')))
			return -1;
		else return 0;
		}
	}
	
function compareVersionRows(sortType,sortOrder) {
	return function(a,b) {
		aVersion = parseInt(a[sortType].replace(".",""));
		bVersion = parseInt(b[sortType].replace(".",""));
		if (((aVersion > bVersion) && (sortOrder == 'Ascending')) || ((aVersion < bVersion) && (sortOrder == 'Descending')))
			return 1;
		else if (((aVersion < bVersion) && (sortOrder == 'Ascending')) || ((aVersion > bVersion) && (sortOrder == 'Descending')))
			return -1;
		else return 0;
		}
	}
	
function sortTable(tableId,sortType,sortOrder,buttonId) {
	a = makeArrayFromTable(tableId);
	if ( sortType == 'Date')
		a.sort(compareDateRows(sortType,sortOrder));
	else if ( sortType == 'Version')
		a.sort(compareVersionRows(sortType,sortOrder));
	else a.sort(compareRows(sortType,sortOrder));
	makeTableFromArray(tableId,a);
	setTableRowAltClass(tableId);
	if (sortOrder == 'Ascending')
		document.getElementById(buttonId).onclick = function () { return sortTable(tableId,sortType,'Descending',buttonId); };
	else if (sortOrder == 'Descending')
		document.getElementById(buttonId).onclick = function () { return sortTable(tableId,sortType,'Ascending',buttonId); };
	}
	
function addRow(tableId) {	
	var t = document.getElementById(tableId);
	var tBody = t.getElementsByTagName('tbody')[0], r, c;
	var rowArray = tBody.getElementsByTagName('tr');
	var inputText = document.getElementById('inputText').value;
	var inputArray = inputText.split(" ");
	numRows = rowArray.length;
	r = tBody.insertRow(numRows);
	c = r.insertCell(0);
	c.innerHTML = inputArray[0];
	c = r.insertCell(1);
	c.innerHTML = inputArray[1];
	document.getElementById('inputText').value = "";
	}
	
function showTableRowsByCellContent(tableId,columnName,cellContent) {
	var t = document.getElementById(tableId);
	var tBody = t.getElementsByTagName('tbody')[0];
	var tableMap = makeObjectMapFromTableHeader(tableId);
	var cellIndex = tableMap.indexOf(columnName);
	for (var i = 0, row; row =tBody.rows[i]; i++) {
		if ((row.cells[cellIndex].innerHTML == cellContent) || (cellContent == 'All')) {
			row.style.display = "table-row";
			}
		else {
			row.style.display = "none";
			}
		}
	}


	
function toggleShowingTableRowsByStatus(tableId,status,buttonId) {
	showTableRowsByCellContent(tableId,'Status',status);
	setTableRowAltClass(tableId);
	if (status == 'Released') {
		document.getElementById(buttonId).onclick = function () { return toggleShowingTableRowsByStatus(tableId,'Review',buttonId); };
		}
	else if (status == 'Review') {
		document.getElementById(buttonId).onclick = function () { return toggleShowingTableRowsByStatus(tableId,'All',buttonId); };
		}
	else if (status == 'All') {
		document.getElementById(buttonId).onclick = function () { return toggleShowingTableRowsByStatus(tableId,'Defunct',buttonId); };
		}
	else if (status == 'Defunct') {
		document.getElementById(buttonId).onclick = function () { return toggleShowingTableRowsByStatus(tableId,'Released',buttonId); };
		}
	// This section of the function checks to see if all rows are hidden
	// If so, it toggles the button again
	var tableBodyRows = document.getElementById(tableId).getElementsByTagName("tbody")[0].getElementsByTagName("tr");
	var numTableBodyRows = tableBodyRows.length;
	var numHiddenTableBodyRows = 0;
	for (var i = 0; i < numTableBodyRows; i++) {
		if (tableBodyRows[i].style['cssText'] == 'display: none;') {
			numHiddenTableBodyRows++;
			}
		}
	if (numHiddenTableBodyRows == numTableBodyRows) {
		document.getElementById(buttonId).click();
		}
	}

function setTableHeaderClickFunctions(tableId, headerRowId) {

        rc = document.getElementById(headerRowId).children
        for (i = 0; i < rc.length; i++) {
            rowHTML = rc[i].innerHTML
            rowId = rc[i].id
            document.getElementById(rc[i].id).onclick = function(t, h, d) {
                return function () { return sortTable(t,h,'Ascending',d);
                    };
                }(tableId, rowHTML, rowId);
            document.getElementById(rc[i].id).style.cursor = "pointer";
            }
        }

// Form verification functions

function verifyFormObject(formObjectID,formObjectType) {
        if (!document.getElementById(formObjectID))
                return false;
        else {
                var objectValue = document.getElementById(formObjectID).value;
                switch(formObjectType) {
                        case 'filename':
                                if (typeof objectValue == 'string') {
                                        var regex = new RegExp('^[a-z0-9._\-]+$','i');
                                        if (regex.test(objectValue))
                                                return true;
                                        else return false;
                                        }
                                else return false;
                                break;
                        case 'alpha':
                                if (typeof objectValue == 'string') {
                                        var regex = new RegExp('^[a-z]+$','i');
                                        if (regex.test(objectValue))
                                                return true;
                                        else return false;
                                        }
                                else return false;
                                break;
                        case 'alphanumeric':
                                if (typeof objectValue == 'string') {
                                        var regex = new RegExp('^[a-z0-9]+$','i');
                                        if (regex.test(objectValue))
                                                return true;
                                        else
                                                return false;
                                        }
                                else return false;
                                break;
						case 'name':
								if (typeof objectValue == 'string') {
										var regex = new RegExp('^[a-z0-9\'\ \-]+$','i');
										if (regex.test(objectValue))
												return true;
										else return false;
										}
								else return false;
								break;
						case 'fulldate':
								if (typeof objectValue == 'string') {
										var regex = new RegExp('^January|February|March|April|May|June|July|August|September|October|November|December, [0-9]+ [0-9]+$','i');
										if (regex.test(objectValue))
												return true;
										else return false; 
										}
								else return false;
								break;
						case 'version':
								if (typeof objectValue == 'string') {
										var regex = new RegExp('^[0-9.]+$','i');
										if (regex.test(objectValue))
												return true;
										else return false;
										}
								else return false;
								break;
                        default:
								return false;
								break;
                        }
                }
        }


function submitForm(formID) {
        var formCheckResult = verifyFormData();
        if (formCheckResult == true)
                document.getElementById(formID).submit();
        else if (formCheckResult == false)
                document.getElementById('submitResult').innerHTML ='There was a problem with the information you entered. Please check and try again.';
        }	
	
// navigation functions

function navigateToNewPage(target) {
	var newPageDropDown = document.getElementById("newPageMenu");
	var newTarget = newPageDropDown.options[newPageDropDown.selectedIndex].value;
	newTarget = target+newTarget;
	window.location.href = newTarget;
	}
	