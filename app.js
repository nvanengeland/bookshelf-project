// Bookshelf App
(function () {
    const PLACEHOLDER_COLORS = [
        '#2d4059', '#ea5455', '#f07b3f', '#3d5a80', '#5c4d7d',
        '#264653', '#2a9d8f', '#e76f51', '#457b9d', '#6d597a',
        '#355070', '#b56576', '#e56b6f', '#bc4749', '#386641',
    ];

    let currentGrade = 'all';
    let allData = [];

    function getBooksPerShelf() {
        if (window.innerWidth <= 390) return 3;
        if (window.innerWidth <= 720) return 4;
        if (window.innerWidth <= 1040) return 5;
        return 7;
    }

    // Load the single shared collection set by data/books.js.
    function loadData() {
        allData = typeof BOOKS_DATA === 'undefined' ? [] : BOOKS_DATA;
    }

    function getBooksForCurrentGrade() {
        if (currentGrade === 'all') return allData;
        return allData.filter(book => Array.isArray(book.grades) && book.grades.includes(currentGrade));
    }

    function groupBooksByAuthor(books) {
        const groups = new Map();

        books.forEach(book => {
            const author = (book.author || '').trim().toLocaleLowerCase('nl');
            if (!groups.has(author)) groups.set(author, []);
            groups.get(author).push(book);
        });

        return [...groups.values()].flat();
    }

    function getFilteredBooks() {
        const books = getBooksForCurrentGrade();
        const search = document.getElementById('search').value.toLowerCase().trim();
        const genreFilter = document.getElementById('genre-filter').value;
        const langFilter = document.getElementById('language-filter').value;
        const pagesFilter = document.getElementById('pages-filter').value;

        const filteredBooks = books.filter(book => {
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

        return groupBooksByAuthor(filteredBooks);
    }

    function populateFilters() {
        const books = getBooksForCurrentGrade();
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

        langSelect.innerHTML = '<option value="">Taal</option>';
        [...languages].sort().forEach(l => {
            langSelect.innerHTML += `<option value="${l}">${l}</option>`;
        });

        // Restore if still valid
        if ([...genres].includes(currentGenre)) genreSelect.value = currentGenre;
        if ([...languages].includes(currentLang)) langSelect.value = currentLang;
    }

    function createBookCard(book, index) {
        const card = document.createElement('button');
        card.type = 'button';
        card.className = 'book-card';
        card.setAttribute('aria-label', `${book.title} door ${book.author}`);
        card.style.setProperty('--delay', `${Math.min(index % 7, 6) * 45}ms`);
        card.style.setProperty('--tilt', `${[-1.2, .4, -.5, .8, -1, .3, -.3][index % 7]}deg`);

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
        return card;
    }

    function renderBookshelf() {
        const container = document.getElementById('bookshelf');
        const books = getFilteredBooks();
        const booksPerShelf = getBooksPerShelf();

        document.getElementById('results-count').textContent = books.length;
        updateClearButton();

        container.innerHTML = '';

        if (books.length === 0) {
            container.innerHTML = '<div class="no-results">Geen boeken gevonden.</div>';
            return;
        }

        // Split books into shelf rows
        for (let i = 0; i < books.length; i += booksPerShelf) {
            const rowBooks = books.slice(i, i + booksPerShelf);

            const row = document.createElement('div');
            row.className = 'shelf-row';
            row.setAttribute('aria-label', `Boekenplank ${Math.floor(i / booksPerShelf) + 1}`);

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

    let modalTrigger = null;

    function showCoverFallback(title) {
        const coverImg = document.getElementById('modal-cover-img');
        const ambientImg = document.getElementById('modal-ambient-img');
        const fallback = document.getElementById('modal-cover-fallback');
        coverImg.style.display = 'none';
        ambientImg.style.display = 'none';
        fallback.textContent = title;
        fallback.style.display = 'flex';
    }

    function updateClearButton() {
        const hasFilters = currentGrade !== 'all' ||
            document.getElementById('search').value.trim() ||
            document.getElementById('genre-filter').value ||
            document.getElementById('language-filter').value ||
            document.getElementById('pages-filter').value;
        document.getElementById('clear-filters').classList.toggle('visible', Boolean(hasFilters));
    }

    function clearFilters() {
        currentGrade = 'all';
        document.getElementById('grade-select').value = 'all';
        document.getElementById('search').value = '';
        document.getElementById('genre-filter').value = '';
        document.getElementById('language-filter').value = '';
        document.getElementById('pages-filter').value = '';
        populateFilters();
        renderBookshelf();
    }

    function openModal(book) {
        const overlay = document.getElementById('modal-overlay');
        const modal = document.getElementById('modal');
        const modalContent = document.getElementById('modal-content');

        modalTrigger = document.activeElement;

        document.getElementById('modal-title').textContent = book.title;
        document.getElementById('modal-author').textContent = book.author;

        const coverImg = document.getElementById('modal-cover-img');
        const ambientImg = document.getElementById('modal-ambient-img');
        const coverFallback = document.getElementById('modal-cover-fallback');
        coverImg.onerror = () => showCoverFallback(book.title);
        if (book.cover_front) {
            coverImg.src = book.cover_front;
            coverImg.alt = `Boekomslag van ${book.title}`;
            coverImg.style.display = 'block';
            ambientImg.src = book.cover_front;
            ambientImg.style.display = 'block';
            coverFallback.style.display = 'none';
        } else {
            showCoverFallback(book.title);
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
            pubLink.style.display = 'inline-flex';
        } else {
            pubLink.style.display = 'none';
        }

        modalContent.scrollTop = 0;
        overlay.classList.add('active');
        overlay.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        modal.focus({ preventScroll: true });
    }

    function closeModal() {
        const overlay = document.getElementById('modal-overlay');
        if (!overlay.classList.contains('active')) return;
        overlay.classList.remove('active');
        overlay.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        if (modalTrigger && typeof modalTrigger.focus === 'function') {
            modalTrigger.focus({ preventScroll: true });
        }
        modalTrigger = null;
    }

    function trapModalFocus(e) {
        const overlay = document.getElementById('modal-overlay');
        if (!overlay.classList.contains('active') || e.key !== 'Tab') return;

        const focusable = [...overlay.querySelectorAll('button:not([disabled]), a[href]:not([style*="display: none"])')]
            .filter(element => element.offsetParent !== null);
        if (!focusable.length) return;

        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (e.shiftKey && document.activeElement === first) {
            e.preventDefault();
            last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
            e.preventDefault();
            first.focus();
        }
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
        toggle.innerHTML = getEffectiveTheme() === 'dark'
            ? '<svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"></circle><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"></path></svg>'
            : '<svg aria-hidden="true" viewBox="0 0 24 24"><path d="M20 15.2A8.4 8.4 0 0 1 8.8 4 8.5 8.5 0 1 0 20 15.2Z"></path></svg>';
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
        document.getElementById('clear-filters').addEventListener('click', clearFilters);

        let resizeTimer;
        let previousShelfSize = getBooksPerShelf();
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                const nextShelfSize = getBooksPerShelf();
                if (nextShelfSize !== previousShelfSize) {
                    previousShelfSize = nextShelfSize;
                    renderBookshelf();
                }
            }, 140);
        });

        // Modal close
        document.getElementById('modal-close').addEventListener('click', closeModal);
        document.getElementById('modal-overlay').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) closeModal();
        });
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeModal();
            trapModalFocus(e);
        });
    });
})();
