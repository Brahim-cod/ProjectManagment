async function fetchOptionsJSON() {
    const response = await fetch('/api/calendar');
    const data = await response.json();
    return data;
}

// fetchOptionsJSON().then((data) => {
//     document.addEventListener('DOMContentLoaded', function() {     
//         var calendarEl = document.getElementById('calendar');
//         let calendar = new FullCalendar.Calendar(calendarEl, data)
//         calendar.render();
//     });
//     console.log(data)
// });



document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    let data = new Date()
    var calendar = new FullCalendar.Calendar(calendarEl, {
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listMonth'
        },
        initialDate: data.toISOString(),
        navLinks: true, // can click day/week names to navigate views
        businessHours: true, // display business hours
        editable: true,
        selectable: true,
        events: [{
                title: 'Business Lunch',
                start: '2022-06-30T13:00:00',
                constraint: 'businessHours'
            },
            {
                title: 'Meeting',
                start: '2022-06-30T11:00:00',
                constraint: 'availableForMeeting', // defined below
                color: '#257e4a'
            },
            {
                title: 'Conference',
                start: '2022-06-30T11:00:00',
                end: '2022-06-30T14:00:00'
            },
            {
                title: 'Party',
                start: '2022-06-26T20:00:00'
            },

            // areas where "Meeting" must be dropped
            {
                groupId: 'availableForMeeting',
                start: '2022-06-11T10:00:00',
                end: '2022-06-11T16:00:00',
                display: 'background'
            },
            {
                groupId: 'availableForMeeting',
                start: '2022-06-30T10:00:00',
                end: '2022-06-30T16:00:00',
                display: 'background'
            },

            // red areas where no events can be dropped
            {
                start: '2022-06-24',
                end: '2022-06-28',
                overlap: false,
                display: 'background',
                color: '#ff9f89'
            },
            {
                start: '2022-09-06',
                end: '2022-09-08',
                overlap: false,
                display: 'background',
                color: '#ff9f89'
            }
        ]
    });

    calendar.render();
});