document.addEventListener('DOMContentLoaded', function() {
    const calculateArrival = () => {
        const departureSelect = document.getElementById('id_departure_airport');
        const arrivalSelect = document.getElementById('id_arrival_airport');
        const departureTime = document.getElementById('id_departure_time').value;
        
        if (departureSelect && arrivalSelect && departureTime && 
            departureSelect.value && arrivalSelect.value) {
            
            const params = new URLSearchParams({
                dep: departureSelect.value,
                arr: arrivalSelect.value,
                time: departureTime
            });
            
            fetch(`/api/calculate-arrival/?${params}`)
                .then(response => response.json())
                .then(data => {
                    if (data.arrival_time) {
                        document.getElementById('id_arrival_time').value = data.arrival_time;
                    }
                })
                .catch(error => console.error('Error:', error));
        }
    };

    // Event listeners
    ['id_departure_airport', 'id_arrival_airport', 'id_departure_time'].forEach(id => {
        document.getElementById(id)?.addEventListener('change', calculateArrival);
    });
});