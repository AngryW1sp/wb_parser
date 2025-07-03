const API_URL = 'http://localhost:8000/api/products/';
const PARSE_URL = 'http://localhost:8000/api/products/parse/';

let allProducts = [];
let products = [];
let priceHistogramChart = null;
let discountVsRatingChart = null;
let currentPage = 1;
let totalPages = 1;
let lastFilters = {};

async function fetchProducts(page = 1) {
    // Сохраняем фильтры для перехода по страницам
    const min_price = document.getElementById('minPrice').value;
    const max_price = document.getElementById('maxPrice').value;
    const min_rating = document.getElementById('minRating').value;
    const min_reviews = document.getElementById('minReviews').value;
    const search_query = document.getElementById('searchQuery').value.trim();

    lastFilters = { min_price, max_price, min_rating, min_reviews, search_query };

    let url = `${API_URL}?page=${page}`;
    if (min_price) url += `&min_price=${min_price}`;
    if (max_price) url += `&max_price=${max_price}`;
    if (min_rating) url += `&min_rating=${min_rating}`;
    if (min_reviews) url += `&min_reviews=${min_reviews}`;
    if (search_query) url += `&request_query=${encodeURIComponent(search_query)}`;

    const resp = await fetch(url);
    const data = await resp.json();
    products = data.results || [];
    currentPage = page;
    totalPages = Math.ceil((data.count || products.length) / 20); // 20 — PAGE_SIZE

    renderTable();
    updateCharts();
    renderPagination();
}

function applyFilters() {
    fetchProducts(1);
}

function renderTable() {
    const tbody = document.querySelector('#productsTable tbody');
    tbody.innerHTML = '';
    products.forEach(p => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${p.title}</td>
            <td>${p.price}</td>
            <td>${p.discounted_price ?? ''}</td>
            <td>${p.rating}</td>
            <td>${p.supplier ?? ''}</td>
            <td>${p.reviews_count}</td>
            <td>${p.search_query}</td>
        `;
        tbody.appendChild(tr);
    });
}

function updateCharts() {
    // Гистограмма цен
    const prices = products.map(p => Number(p.price)).filter(Boolean);
    if (prices.length === 0) return;

    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const binsCount = 10;
    const step = Math.ceil((max - min) / binsCount) || 1;
    const bins = Array(binsCount).fill(0);
    prices.forEach(price => {
        let idx = Math.floor((price - min) / step);
        if (idx >= bins.length) idx = bins.length - 1;
        bins[idx]++;
    });
    const labels = bins.map((_, i) => `${min + i * step} - ${min + (i + 1) * step}`);

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

    // Скидка vs Рейтинг
    const points = products
        .filter(p => p.price && p.discounted_price && p.rating !== null)
        .map(p => ({
            x: Number(p.rating),
            y: Number(p.price) - Number(p.discounted_price)
        }));

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

// --- Новые функции для парсинга ---
function showParseForm() {
    document.getElementById('parseForm').style.display = '';
}
function hideParseForm() {
    document.getElementById('parseForm').style.display = 'none';
    document.getElementById('parseStatus').textContent = '';
}
async function startParsing() {
    const query = document.getElementById('parseQuery').value;
    const category = document.getElementById('parseCategory').value;
    const pages = document.getElementById('parsePages').value;
    if (!query && !category) {
        document.getElementById('parseStatus').textContent = 'Укажите query или category_url!';
        return;
    }
    document.getElementById('parseStatus').textContent = 'Парсинг запущен...';
    const resp = await fetch(PARSE_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query, category_url: category, pages: pages })
    });
    const data = await resp.json();
    if (resp.ok) {
        document.getElementById('parseStatus').textContent = 'Парсинг запущен! Task ID: ' + data.task_id;
        // После парсинга — загружаем только новые результаты
        setTimeout(async () => {
            await fetchProducts();
            // Оставляем только товары с этим запросом/категорией
            if (query) {
                document.getElementById('searchQuery').value = query;
            } else if (category) {
                document.getElementById('searchQuery').value = category;
            }
            applyFilters();
        }, 3000); // Можно увеличить задержку, если парсинг долгий
        hideParseForm();
    } else {
        document.getElementById('parseStatus').textContent = data.error || 'Ошибка запуска парсинга';
    }
}

function renderPagination() {
    const container = document.getElementById('pagination');
    if (!container) return;
    container.innerHTML = '';

    if (totalPages <= 1) return;

    const prevBtn = document.createElement('button');
    prevBtn.textContent = 'Назад';
    prevBtn.disabled = currentPage === 1;
    prevBtn.onclick = () => fetchProducts(currentPage - 1);
    container.appendChild(prevBtn);

    const info = document.createElement('span');
    info.textContent = ` Страница ${currentPage} из ${totalPages} `;
    container.appendChild(info);

    const nextBtn = document.createElement('button');
    nextBtn.textContent = 'Вперёд';
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.onclick = () => fetchProducts(currentPage + 1);
    container.appendChild(nextBtn);
}

window.onload = function() {
    fetchProducts(1);
};