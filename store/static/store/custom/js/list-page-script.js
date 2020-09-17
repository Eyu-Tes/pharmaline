/* make table responsive */
function makeTableResponsive(dataTableWrapper){
    let table = dataTableWrapper.querySelector('table');
    let tableContainer = table.parentElement;

    let resoponsiveTableContainer = document.createElement('div');
    resoponsiveTableContainer.className = 'responsive-table-container';

    resoponsiveTableContainer.appendChild(table);
    tableContainer.appendChild(resoponsiveTableContainer);
}

// removes wrapper (patent element) without removing child
function unwrap(wrapper) {
    // place childNodes in document fragment
    var docFrag = document.createDocumentFragment();
    while (wrapper.firstChild) {
        var child = wrapper.removeChild(wrapper.firstChild);
        docFrag.appendChild(child);
    }

    // replace wrapper with document fragment
    wrapper.parentNode.replaceChild(docFrag, wrapper);
}

function buildTable(dataTableWrapper) {
    let inputElm = dataTableWrapper.querySelector('#dtBasicExample_filter input');
    inputElm.className = "form-control form-control-lg border-primary d-block";

    // remove label element wrapping the input element
    unwrap(inputElm.parentElement);

    // insert add section
    let addSectionContainer = dataTableWrapper.querySelector('.row:first-child div:first-child');
    let addSection = document.querySelector('#add-section');
    addSectionContainer.appendChild(addSection);
    addSection.classList.remove('d-none');

    // make table responsive
    makeTableResponsive(dataTableWrapper);

    // display table container
    let tableContainer = document.querySelector('.table-container'); 
    tableContainer.classList.remove('d-none');
}

/* wait until data table wrapper is loaded from mdb's datatables.min.css */
var checkExist = setInterval(function() {
    let dtw = document.querySelector('#dtBasicExample_wrapper');
    if (dtw) {
        clearInterval(checkExist);
        buildTable(dtw);
    }
}, 5); // check every 5 milliseconds
