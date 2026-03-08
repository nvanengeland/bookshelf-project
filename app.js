// Bookshelf App
(function () {
    const BOOKS_PER_SHELF = 7;
    const PLACEHOLDER_COLORS = [
        '#2d4059', '#ea5455', '#f07b3f', '#3d5a80', '#5c4d7d',
        '#264653', '#2a9d8f', '#e76f51', '#457b9d', '#6d597a',
        '#355070', '#b56576', '#e56b6f', '#bc4749', '#386641',
    ];

    let currentGrade = 'graad_1';
    let allData = {};

    // Load data from global variables set by the JS data files
    function loadData() {
        if (typeof GRAAD_1_DATA !== 'undefined') allData.graad_1 = GRAAD_1_DATA;
        if (typeof GRAAD_2_DATA !== 'undefined') allData.graad_2 = GRAAD_2_DATA;
        if (typeof GRAAD_3_DATA !== 'undefined') allData.graad_3 = GRAAD_3_DATA;
    }

    function getFilteredBooks() {
        const books = allData[currentGrade] || [];
        const search = document.getElementById('search').value.toLowerCase().trim();
        const genreFilter = document.getElementById('genre-filter').value;
        const langFilter = document.getElementById('language-filter').value;
        const pagesFilter = document.getElementById('pages-filter').value;

        return books.filter(book => {
            if (search && !book.title.toLowerCase().includes(search) &&
                !book.author.toLowerCase().includes(search)) {
                return false;
            }
            if (genreFilter && (!book.genre || !book.genre.toLowerCase().includes(genreFilter.toLowerCase()))) {
                return false;
            }
            if (langFilter && book.original_language !== langFilter) {
                return false;
            }
            if (pagesFilter) {
                const [min, max] = pagesFilter.split('-').map(Number);
                const pages = parseInt(book.pages, 10);
                if (!pages || pages < min || pages > max) return false;
            }
            return true;
        });
    }

    function populateFilters() {
        const books = allData[currentGrade] || [];
        const genres = new Set();
        const languages = new Set();

        books.forEach(b => {
            if (b.genre) {
                b.genre.split(',').forEach(g => {
                    const trimmed = g.trim();
                    if (trimmed) genres.add(trimmed);
                });
            }
            if (b.original_language) languages.add(b.original_language);
        });

        const genreSelect = document.getElementById('genre-filter');
        const langSelect = document.getElementById('language-filter');

        // Save current values
        const currentGenre = genreSelect.value;
        const currentLang = langSelect.value;

        genreSelect.innerHTML = '<option value="">Alle genres</option>';
        [...genres].sort().forEach(g => {
            genreSelect.innerHTML += `<option value="${g}">${g}</option>`;
        });

        langSelect.innerHTML = '<option value="">Alle talen</option>';
        [...languages].sort().forEach(l => {
            langSelect.innerHTML += `<option value="${l}">${l}</option>`;
        });

        // Restore if still valid
        if ([...genres].includes(currentGenre)) genreSelect.value = currentGenre;
        if ([...languages].includes(currentLang)) langSelect.value = currentLang;
    }

    function createBookCard(book, index) {
        const card = document.createElement('div');
        card.className = 'book-card';
        card.setAttribute('role', 'button');
        card.setAttribute('tabindex', '0');
        card.setAttribute('aria-label', `${book.title} door ${book.author}`);

        const colorIdx = (index * 7 + index) % PLACEHOLDER_COLORS.length;
        const color = PLACEHOLDER_COLORS[colorIdx];

        if (book.cover_front) {
            card.innerHTML = `
                <div class="book-spine"></div>
                <img class="book-cover" src="${book.cover_front}" alt="${book.title}"
                     onerror="this.outerHTML='<div class=\\'book-cover-placeholder\\' style=\\'background:${color}\\'><span>${escapeHtml(book.title)}</span><span class=\\'placeholder-author\\'>${escapeHtml(book.author)}</span></div>'">
                <div class="book-label">${escapeHtml(book.title)}</div>
            `;
        } else {
            card.innerHTML = `
                <div class="book-spine"></div>
                <div class="book-cover-placeholder" style="background:${color}">
                    <span>${escapeHtml(book.title)}</span>
                    <span class="placeholder-author">${escapeHtml(book.author)}</span>
                </div>
                <div class="book-label">${escapeHtml(book.title)}</div>
            `;
        }

        card.addEventListener('click', () => openModal(book));
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openModal(book);
            }
        });

        return card;
    }

    function renderBookshelf() {
        const container = document.getElementById('bookshelf');
        const books = getFilteredBooks();

        container.innerHTML = '';

        if (books.length === 0) {
            container.innerHTML = '<div class="no-results">Geen boeken gevonden.</div>';
            return;
        }

        // Split books into shelf rows
        for (let i = 0; i < books.length; i += BOOKS_PER_SHELF) {
            const rowBooks = books.slice(i, i + BOOKS_PER_SHELF);

            const row = document.createElement('div');
            row.className = 'shelf-row';

            const booksContainer = document.createElement('div');
            booksContainer.className = 'shelf-books';

            rowBooks.forEach((book, idx) => {
                booksContainer.appendChild(createBookCard(book, i + idx));
            });

            const plank = document.createElement('div');
            plank.className = 'shelf-plank';

            row.appendChild(booksContainer);
            row.appendChild(plank);
            container.appendChild(row);
        }
    }

    function openModal(book) {
        const overlay = document.getElementById('modal-overlay');

        document.getElementById('modal-title').textContent = book.title;
        document.getElementById('modal-author').textContent = book.author;

        const coverImg = document.getElementById('modal-cover-img');
        if (book.cover_front) {
            coverImg.src = book.cover_front;
            coverImg.style.display = 'block';
        } else {
            coverImg.style.display = 'none';
        }

        document.getElementById('modal-pages').textContent = book.pages ? `${book.pages} pagina's` : '';
        document.getElementById('modal-year').textContent = book.publication_date ? `${book.publication_date}` : '';
        document.getElementById('modal-language').textContent = book.original_language || '';

        const genreContainer = document.getElementById('modal-genre');
        genreContainer.innerHTML = '';
        if (book.genre) {
            book.genre.split(',').forEach(g => {
                const trimmed = g.trim();
                if (trimmed) {
                    genreContainer.innerHTML += `<span>${escapeHtml(trimmed)}</span>`;
                }
            });
        }

        document.getElementById('modal-synopsis').textContent = book.synopsis || '';
        document.getElementById('modal-publisher').textContent = book.publisher ? `Uitgever: ${book.publisher}` : '';
        document.getElementById('modal-isbn').textContent = book.isbn ? `ISBN: ${book.isbn}` : '';

        const pubLink = document.getElementById('modal-publisher-link');
        if (book.publisher_url) {
            pubLink.href = book.publisher_url;
            pubLink.style.display = 'inline-block';
        } else {
            pubLink.style.display = 'none';
        }

        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        document.getElementById('modal-overlay').classList.remove('active');
        document.body.style.overflow = '';
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    // Theme toggle
    function initTheme() {
        const saved = localStorage.getItem('theme');
        const toggle = document.getElementById('theme-toggle');

        if (saved) {
            document.documentElement.setAttribute('data-theme', saved);
        }
        // else: no data-theme → CSS @media prefers-color-scheme decides

        updateToggleIcon();

        toggle.addEventListener('click', () => {
            const isDark = getEffectiveTheme() === 'dark';
            const next = isDark ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            updateToggleIcon();
        });
    }

    function getEffectiveTheme() {
        const explicit = document.documentElement.getAttribute('data-theme');
        if (explicit) return explicit;
        return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    }

    function updateToggleIcon() {
        const toggle = document.getElementById('theme-toggle');
        toggle.innerHTML = getEffectiveTheme() === 'dark' ? '&#9788;' : '&#9790;';
    }

    // Event listeners
    document.addEventListener('DOMContentLoaded', () => {
        loadData();
        populateFilters();
        renderBookshelf();
        initTheme();

        // Grade dropdown
        document.getElementById('grade-select').addEventListener('change', (e) => {
            currentGrade = e.target.value;
            document.getElementById('search').value = '';
            populateFilters();
            renderBookshelf();
        });

        // Filters
        document.getElementById('search').addEventListener('input', renderBookshelf);
        document.getElementById('genre-filter').addEventListener('change', renderBookshelf);
        document.getElementById('language-filter').addEventListener('change', renderBookshelf);
        document.getElementById('pages-filter').addEventListener('change', renderBookshelf);

        // Modal close
        document.getElementById('modal-close').addEventListener('click', closeModal);
        document.getElementById('modal-overlay').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) closeModal();
        });
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeModal();
        });
    });
})();
