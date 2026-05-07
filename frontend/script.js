// 1. Configuration: Set the API URL based on environment
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'
    : 'https://YOUR-APP.onrender.com'; // Change this once deployed

// 2. Full Neighborhood Data
const allNeighborhoods = [
    "Al Barari", "Al Barsha", "Al Furjan", "Al Khalfan", "Al Quoz", "Al Sufouh",
    "Al Warqaa", "Arjan", "Barsha Heights", "Bluewaters", "Business Bay",
    "Culture Village", "Damac Hills", "Discovery Gardens", "Downtown Dubai",
    "Dubai Creek Harbour", "Dubai Harbour", "Dubai Hills Estate", "Dubai Land",
    "Dubai Marina", "Dubai Production City", "Dubai Science City", "Dubai Silicon Oasis",
    "Dubai South", "Dubai Sports City", "Dubai Studio City", "Dubai World Central",
    "Falcon City of Wonders", "Green Community", "International City", "Jumeirah",
    "Jumeirah Beach Residence", "Jumeirah Golf Estates", "Jumeirah Heights",
    "Jumeirah Islands", "Jumeirah Lake Towers", "Jumeirah Park", "Jumeirah Village Circle",
    "Jumeirah Village Triangle", "Living Legends", "Meydan", "Mina Rashid",
    "Mirdif", "Mohammed Bin Rashid City", "Motor City", "Mudon", "Old Town",
    "Palm Jumeirah", "Remraam", "Serena", "Sheikh Zayed Road", "The Views",
    "The Villa", "Town Square", "World Islands"
];

// Select DOM elements
const nbhdList = document.getElementById('nbhdList');
const nbhdSearch = document.getElementById('nbhdSearch');
const hiddenInput = document.getElementById('neighborhood');
const predictionForm = document.getElementById('predictionForm');
const btn = document.getElementById('predictBtn');

// 3. Dropdown Logic
function populateNeighborhoods() {
    nbhdList.innerHTML = "";
    allNeighborhoods.forEach(name => {
        const li = document.createElement('li');
        li.textContent = name;
        li.onclick = () => selectNbhd(name);
        nbhdList.appendChild(li);
    });
}

function filterList() {
    const filter = nbhdSearch.value.toUpperCase();
    const li = nbhdList.getElementsByTagName('li');
    for (let i = 0; i < li.length; i++) {
        let txtValue = li[i].textContent || li[i].innerText;
        li[i].style.display = txtValue.toUpperCase().indexOf(filter) > -1 ? "" : "none";
    }
}

function showList() {
    nbhdList.classList.remove('hidden');
}

function selectNbhd(val) {
    nbhdSearch.value = val;
    hiddenInput.value = val;
    nbhdList.classList.add('hidden');
}

// 4. Prediction Form Logic
predictionForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    // UI Feedback
    btn.innerText = "Calculating...";
    btn.disabled = true;

    const payload = {
        neighborhood: hiddenInput.value,
        size_in_sqft: parseFloat(document.getElementById('size').value),
        no_of_bedrooms: parseInt(document.getElementById('bedrooms').value),
        no_of_bathrooms: parseInt(document.getElementById('bathrooms').value),
        quality: document.getElementById('quality').value
    };

    try {
        // Note: Using the dynamic API_URL variable here
        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.formatted) {
            document.getElementById('result').classList.remove('hidden');
            document.getElementById('priceText').innerText = data.formatted;

            // Smooth scroll to result
            document.getElementById('result').scrollIntoView({ behavior: 'smooth' });
        }
    } catch (err) {
        console.error("Fetch error:", err);
        alert("Could not connect to the server. Is your Flask app running?");
    } finally {
        btn.innerText = "Estimate Price";
        btn.disabled = false;
    }
});

// Close list when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.searchable-dropdown')) {
        nbhdList.classList.add('hidden');
    }
});

// Initialize the list
populateNeighborhoods();

// Global assignments for HTML inline events (onfocus/onkeyup)
window.showList = showList;
window.filterList = filterList;