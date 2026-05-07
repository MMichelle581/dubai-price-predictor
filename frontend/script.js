// --- NEIGHBORHOOD SEARCH LOGIC ---
function showList() {
    document.getElementById('nbhdList').classList.remove('hidden');
}

function filterList() {
    const input = document.getElementById('nbhdSearch');
    const filter = input.value.toUpperCase();
    const li = document.getElementById('nbhdList').getElementsByTagName('li');

    for (let i = 0; i < li.length; i++) {
        let txtValue = li[i].textContent || li[i].innerText;
        li[i].style.display = txtValue.toUpperCase().indexOf(filter) > -1 ? "" : "none";
    }
}

function selectNbhd(val) {
    document.getElementById('nbhdSearch').value = val;
    document.getElementById('neighborhood').value = val; // Sets hidden value for Flask
    document.getElementById('nbhdList').classList.add('hidden');
}

// Close dropdown if user clicks outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.searchable-dropdown')) {
        document.getElementById('nbhdList').classList.add('hidden');
    }
});

// --- ESTIMATION LOGIC ---
document.getElementById('predictionForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('predictBtn');
    const resultDiv = document.getElementById('result');

    btn.innerText = "Processing...";
    btn.disabled = true;

    const payload = {
        neighborhood: document.getElementById('neighborhood').value,
        size_in_sqft: parseFloat(document.getElementById('size').value),
        no_of_bedrooms: parseInt(document.getElementById('bedrooms').value),
        no_of_bathrooms: parseInt(document.getElementById('bathrooms').value),
        quality: document.getElementById('quality').value
    };

    try {
        const response = await fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (data.formatted) {
            resultDiv.classList.remove('hidden');
            document.getElementById('priceText').innerText = data.formatted;
        }
    } catch (err) {
        console.error("API Error:", err);
        alert("Server error. Make sure your Flask app is running!");
    } finally {
        btn.innerText = "Estimate Price";
        btn.disabled = false;
    }
});