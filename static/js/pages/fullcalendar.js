async function fetchOptionsJSON() {
    const response = await fetch('/api/calendar');
    const data = await response.json();
    return data;
}

console.log('test2')
fetchOptionsJSON().then((data) => {
    document.addEventListener('DOMContentLoaded', function() {     
        var calendarEl = document.getElementById('calendar');
        let calendar = new FullCalendar.Calendar(calendarEl, data)
        calendar.render();
    });
    console.log(data)
});

// fetchOptionsJSON().then((data) => {
//     document.addEventListener('DOMContentLoaded', function() {
//         var calendarEl = document.getElementById('calendar');
//         let calendar = new FullCalendar.Calendar(calendarEl, data)
//         calendar.render();
//     });
// });


