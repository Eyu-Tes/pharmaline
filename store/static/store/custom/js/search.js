let searchInput = document.querySelector('input[type=search]');
let rows = document.querySelectorAll("tbody tr");

searchInput.addEventListener('keyup', function () {
        q = this.value.trim().toLowerCase();
        rows.forEach((row) => {
            row.querySelector('td#name').textContent.trim().toLowerCase().includes(q) 
            ? (row.style.display = 'table-row') : (row.style.display = 'none');
        });
});
