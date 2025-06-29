const API_URL = "http://localhost:8000/api/products/";
const PARSE_URL = "http://localhost:8000/api/products/parse/";

let products = [];
let sortField = null;
let sortOrder = 1; // 1 - по возрастанию, -1 - по убыванию

document.getElementById('parseForm').onsubmit = async function (e) {
    e.preventDefault();
    const query = document.getElementById('query').value.trim();
    const category_url = document.getElementById('category_url').value.trim();
    const statusSpan = document.getElementById('parseStatus');
    statusSpan.textContent = "Парсинг...";
    statusSpan.className = "";

    if (!query && !category_url) {
        statusSpan.textContent = "Введите запрос или ссылку на категорию!";
        statusSpan.className = "error";
        return;
    }

    try {
        const resp = await fetch(PARSE_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query, category_url })
        });
        const data = await resp.json();
        if (resp.ok) {
            statusSpan.textContent = "Парсинг завершён!";
            fetchProducts();
        } else {
            statusSpan.textContent = data.error || "Ошибка парсинга";
            statusSpan.className = "error";
        }
    } catch (err) {
        statusSpan.textContent = "Ошибка сети";
        statusSpan.className = "error";
    }
};

async function fetchProducts() {
    const min_price = document.getElementById('minPrice').value;
    const max_price = document.getElementById('maxPrice').value;
    const min_rating = document.getElementById('minRating').value;
    const min_reviews = document.getElementById('minReviews').value;
    const request_query = document.getElementById('requestQuerySelect').value;

    let url = `${API_URL}?min_price=${min_price}&max_price=${max_price}&min_rating=${min_rating}&min_reviews=${min_reviews}`;
    if (request_query) {
        url += `&request_query=${encodeURIComponent(request_query)}`;
    }
    if (sortField) {
        url += `&ordering=${sortOrder === 1 ? '' : '-'}${sortField}`;
    }

    const resp = await fetch(url);
    products = await resp.json();
    renderTable();
}

function renderTable() {
    const tbody = document.querySelector("#productsTable tbody");
    tbody.innerHTML = "";
    products.forEach(prod => {
        tbody.innerHTML += `
            <tr>
                <td>${prod.title}</td>
                <td>${prod.price}</td>
                <td>${prod.discounted_price ?? '-'}</td>
                <td>${prod.rating}</td>
                <td>${prod.reviews_count}</td>
            </tr>
        `;
    });
}
let priceHistogramChart = null;
let discountVsRatingChart = null;

function updateCharts() {
    // --- Гистограмма цен ---
    // 1. Собираем цены
    const prices = products.map(p => Number(p.price));
    // 2. Определяем диапазоны (например, шаг 1000)
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const step = Math.ceil((max - min) / 10) || 1;
    const bins = Array(10).fill(0);
    prices.forEach(price => {
        let idx = Math.floor((price - min) / step);
        if (idx >= bins.length) idx = bins.length - 1;
        bins[idx]++;
    });
    const labels = bins.map((_, i) => `${min + i * step} - ${min + (i + 1) * step}`);

    // 3. Рисуем/обновляем гистограмму
    if (priceHistogramChart) priceHistogramChart.destroy();
    const ctx1 = document.getElementById('priceHistogram').getContext('2d');
    priceHistogramChart = new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Количество товаров',
                data: bins,
                backgroundColor: '#1976d2'
            }]
        },
        options: {
            responsive: false,
            plugins: { legend: { display: false } }
        }
    });

    // --- Линейный график скидка vs рейтинг ---
    // 1. Собираем данные
    const points = products
        .filter(p => p.price && p.discounted_price && p.rating !== null)
        .map(p => ({
            x: Number(p.rating),
            y: Number(p.price) - Number(p.discounted_price)
        }));

    // 2. Рисуем/обновляем график
    if (discountVsRatingChart) discountVsRatingChart.destroy();
    const ctx2 = document.getElementById('discountVsRating').getContext('2d');
    discountVsRatingChart = new Chart(ctx2, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Скидка vs Рейтинг',
                data: points,
                backgroundColor: '#e53935'
            }]
        },
        options: {
            responsive: false,
            scales: {
                x: { title: { display: true, text: 'Рейтинг' }, min: 0, max: 5 },
                y: { title: { display: true, text: 'Скидка (руб.)' } }
            }
        }
    });
}

function sortTable(field) {
    if (sortField === field) {
        sortOrder *= -1;
    } else {
        sortField = field;
        sortOrder = 1;
    }
    fetchProducts();
}
async function loadRequestQueries() {
    const resp = await fetch("http://localhost:8000/api/products/queries/");
    const queries = await resp.json();
    const select = document.getElementById('requestQuerySelect');
    select.innerHTML = '<option value="">Все</option>';
    queries.forEach(q => {
        const opt = document.createElement('option');
        opt.value = q;
        opt.textContent = q;
        select.appendChild(opt);
    });
}

// Вызвать при загрузке страницы
window.onload = function() {
    loadRequestQueries();
    fetchProducts();
    renderTable();
    updateCharts();
};

// Загрузка товаров при открытии страницы
window.onload = fetchProducts;