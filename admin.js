(function () {
    const GRADE_META = {
        graad_1: { label: '1ste graad' },
        graad_2: { label: '2de graad' },
        graad_3: { label: '3de graad' },
    };
    const DATA_FILE = 'books.js';

    const FIELD_NAMES = [
        'title', 'author', 'isbn', 'pages', 'publication_date',
        'original_language', 'genre', 'publisher', 'synopsis',
        'cover_front', 'age_category', 'publisher_url',
    ];

    let data = clone(typeof BOOKS_DATA === 'undefined' ? [] : BOOKS_DATA);
    let activeGrade = 'graad_1';
    let activeBook = null;
    let projectDirectory = null;
    let isDirty = false;
    let toastTimer = null;
    const pendingCovers = new WeakMap();

    const form = document.getElementById('book-form');
    const list = document.getElementById('book-list');
    const search = document.getElementById('book-search');
    const coverImage = document.getElementById('cover-image');
    const coverPlaceholder = document.getElementById('cover-placeholder');

    function clone(value) {
        return JSON.parse(JSON.stringify(value));
    }

    function normaliseBook(book) {
        return {
            grades: normaliseGrades(book.grades),
            title: stringValue(book.title),
            author: stringValue(book.author),
            isbn: stringValue(book.isbn),
            pages: numberValue(book.pages),
            publication_date: numberValue(book.publication_date),
            original_language: stringValue(book.original_language),
            genre: stringValue(book.genre),
            publisher: stringValue(book.publisher),
            synopsis: stringValue(book.synopsis),
            cover_front: nullableString(book.cover_front),
            cover_back: nullableString(book.cover_back),
            age_category: stringValue(book.age_category),
            publisher_url: nullableString(book.publisher_url),
        };
    }

    function normaliseGrades(grades) {
        const values = Array.isArray(grades) ? grades : [grades];
        return [...new Set(values.filter((grade) => Object.hasOwn(GRADE_META, grade)))];
    }

    function stringValue(value) {
        return value === null || value === undefined ? '' : String(value).trim();
    }

    function nullableString(value) {
        const result = stringValue(value);
        return result || null;
    }

    function numberValue(value) {
        if (value === '' || value === null || value === undefined) return null;
        const parsed = Number.parseInt(value, 10);
        return Number.isFinite(parsed) ? parsed : null;
    }

    function renderCounts() {
        Object.keys(GRADE_META).forEach((grade) => {
            document.getElementById(`count-${grade}`).textContent = data.filter((book) => book.grades.includes(grade)).length;
        });
    }

    function renderList() {
        renderCounts();
        list.replaceChildren();
        const query = search.value.toLocaleLowerCase('nl').trim();
        const books = data
            .filter((book) => book.grades.includes(activeGrade))
            .filter((book) => !query || `${book.title} ${book.author}`.toLocaleLowerCase('nl').includes(query))
            .sort((a, b) => stringValue(a.title).localeCompare(stringValue(b.title), 'nl'));

        if (!books.length) {
            const empty = document.createElement('p');
            empty.className = 'book-list-empty';
            empty.textContent = query ? 'Geen boeken gevonden.' : 'Nog geen boeken in deze graad.';
            list.appendChild(empty);
            return;
        }

        books.forEach((book) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = `book-list-item${book === activeBook ? ' active' : ''}`;

            const cover = createListCover(book);
            const copy = document.createElement('span');
            copy.className = 'book-list-copy';
            const title = document.createElement('strong');
            title.textContent = book.title || 'Naamloos boek';
            const author = document.createElement('small');
            author.textContent = book.author || 'Geen auteur';
            copy.append(title, author);

            const arrow = document.createElement('span');
            arrow.className = 'book-list-arrow';
            arrow.textContent = '›';
            button.append(cover, copy, arrow);
            button.addEventListener('click', () => selectBook(book));
            list.appendChild(button);
        });
    }

    function createListCover(book) {
        const pending = pendingCovers.get(book);
        if (pending || book.cover_front) {
            const image = document.createElement('img');
            image.className = 'book-list-cover';
            image.alt = '';
            image.src = pending ? pending.previewUrl : book.cover_front;
            image.addEventListener('error', () => image.replaceWith(createFallback(book)));
            return image;
        }
        return createFallback(book);
    }

    function createFallback(book) {
        const fallback = document.createElement('span');
        fallback.className = 'book-list-cover book-list-fallback';
        fallback.textContent = (book.title || 'B').charAt(0).toUpperCase();
        return fallback;
    }

    function selectBook(book) {
        activeBook = book;
        form.hidden = false;
        document.getElementById('empty-state').hidden = true;
        FIELD_NAMES.forEach((name) => {
            form.elements[name].value = book[name] ?? '';
        });
        gradeCheckboxes().forEach((checkbox) => {
            checkbox.checked = book.grades.includes(checkbox.value);
        });
        updateEditorHeading();
        updateSynopsisCount();
        updateCoverPreview();
        renderList();
        if (window.innerWidth <= 680) form.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function gradeCheckboxes() {
        return [...form.querySelectorAll('input[name="grades"]')];
    }

    function updateEditorHeading() {
        document.getElementById('editor-title').textContent = activeBook && activeBook.title
            ? activeBook.title
            : 'Nieuw boek';
    }

    function updateSynopsisCount() {
        document.getElementById('synopsis-count').textContent = form.elements.synopsis.value.length;
    }

    function updateCoverPreview() {
        if (!activeBook) return;
        const pending = pendingCovers.get(activeBook);
        const source = pending ? pending.previewUrl : form.elements.cover_front.value.trim();
        coverImage.hidden = !source;
        coverPlaceholder.hidden = Boolean(source);
        if (source) coverImage.src = source;
    }

    function updateBookFromForm() {
        if (!activeBook) return;
        FIELD_NAMES.forEach((name) => {
            const value = form.elements[name].value;
            if (name === 'pages' || name === 'publication_date') {
                activeBook[name] = numberValue(value);
            } else if (name === 'cover_front' || name === 'publisher_url') {
                activeBook[name] = nullableString(value);
            } else {
                activeBook[name] = stringValue(value);
            }
        });
        activeBook.grades = gradeCheckboxes()
            .filter((checkbox) => checkbox.checked)
            .map((checkbox) => checkbox.value);
    }

    function setDirty() {
        isDirty = true;
        const state = document.getElementById('save-state');
        state.textContent = 'Niet-opgeslagen wijzigingen';
        state.classList.add('dirty');
    }

    function setClean() {
        isDirty = false;
        const state = document.getElementById('save-state');
        state.textContent = 'Alles is bijgewerkt';
        state.classList.remove('dirty');
    }

    function addBook() {
        const book = normaliseBook({ grades: [activeGrade], title: '', author: '' });
        data.unshift(book);
        search.value = '';
        selectBook(book);
        setDirty();
        form.elements.title.focus();
    }

    function deleteBook() {
        if (!activeBook) return;
        const label = activeBook.title || 'dit boek';
        if (!window.confirm(`Wil je “${label}” echt verwijderen?`)) return;
        data = data.filter((book) => book !== activeBook);
        activeBook = null;
        form.hidden = true;
        document.getElementById('empty-state').hidden = false;
        setDirty();
        renderList();
        showToast('Boek verwijderd. Sla nog op om dit definitief te maken.');
    }

    async function chooseProjectFolder() {
        if (isDirty && !window.confirm('Je hebt nog niet-opgeslagen wijzigingen. Wil je toch een andere projectmap openen?')) {
            return;
        }
        if (!('showDirectoryPicker' in window)) {
            showToast('Deze browser ondersteunt geen maptoegang. Bij opslaan wordt het databestand gedownload.', true);
            return;
        }

        try {
            const directory = await window.showDirectoryPicker({ mode: 'readwrite' });
            const dataDirectory = await directory.getDirectoryHandle('data');
            await directory.getDirectoryHandle('covers');
            const handle = await dataDirectory.getFileHandle(DATA_FILE);
            const text = await (await handle.getFile()).text();
            const freshData = parseDataFile(text).map(normaliseBook);

            projectDirectory = directory;
            data = freshData;
            activeBook = null;
            form.hidden = true;
            document.getElementById('empty-state').hidden = false;
            document.getElementById('storage-explanation').textContent = `Wijzigingen worden rechtstreeks bewaard in “${directory.name}”.`;
            document.getElementById('side-folder-button').textContent = 'Andere projectmap';
            document.getElementById('folder-button').textContent = directory.name;
            setClean();
            renderList();
            showToast(`Projectmap “${directory.name}” geopend.`);
        } catch (error) {
            if (error.name !== 'AbortError') {
                showToast('Dit lijkt niet de juiste projectmap. Kies de map met “data” en “covers”.', true);
            }
        }
    }

    function parseDataFile(text) {
        const start = text.indexOf('[');
        const end = text.lastIndexOf(']');
        if (start < 0 || end < start) throw new Error('Ongeldig databestand');
        return JSON.parse(text.slice(start, end + 1));
    }

    function serialiseData() {
        const books = data.map(normaliseBook);
        return `const BOOKS_DATA = ${JSON.stringify(books, null, 2)};\n`;
    }

    async function saveAll() {
        updateBookFromForm();
        const incomplete = findIncompleteBook();
        if (incomplete) {
            activeGrade = incomplete.book.grades[0] || activeGrade;
            document.querySelectorAll('.grade-tab').forEach((tab) => {
                tab.classList.toggle('active', tab.dataset.grade === activeGrade);
            });
            selectBook(incomplete.book);
            if (incomplete.field === 'grades') {
                gradeCheckboxes()[0].focus();
                showToast(`Kies minstens één graad voor “${incomplete.book.title || 'het nieuwe boek'}”.`, true);
            } else {
                form.elements[incomplete.field].focus();
                showToast(`Geef “${incomplete.book.title || 'het nieuwe boek'}” eerst een ${incomplete.field === 'title' ? 'titel' : 'auteur'}.`, true);
            }
            return;
        }

        try {
            if (projectDirectory) {
                await saveToProjectFolder();
                setClean();
                const time = new Intl.DateTimeFormat('nl-BE', { hour: '2-digit', minute: '2-digit' }).format(new Date());
                document.getElementById('last-saved').textContent = `Laatst opgeslagen om ${time}`;
                showToast('Alle wijzigingen zijn opgeslagen.');
            } else {
                downloadDataFile();
                const coverCount = downloadPendingCovers();
                setClean();
                showToast(coverCount
                    ? `Het databestand en ${coverCount} cover${coverCount === 1 ? '' : 's'} zijn gedownload.`
                    : 'Het databestand is gedownload. Plaats het in de map “data”.');
            }
        } catch (error) {
            showToast(`Opslaan is niet gelukt: ${error.message}`, true);
        }
    }

    async function saveToProjectFolder() {
        const permission = await projectDirectory.requestPermission({ mode: 'readwrite' });
        if (permission !== 'granted') throw new Error('geen schrijftoegang tot de map');
        const coversDirectory = await projectDirectory.getDirectoryHandle('covers', { create: true });
        for (const book of data) {
            const pending = pendingCovers.get(book);
            if (!pending) continue;
            const coverHandle = await coversDirectory.getFileHandle(pending.fileName, { create: true });
            await writeFile(coverHandle, pending.file);
            URL.revokeObjectURL(pending.previewUrl);
            pendingCovers.delete(book);
        }
        const dataDirectory = await projectDirectory.getDirectoryHandle('data');
        const handle = await dataDirectory.getFileHandle(DATA_FILE, { create: true });
        await writeFile(handle, serialiseData());
        updateCoverPreview();
        renderList();
    }

    function findIncompleteBook() {
        for (const book of data) {
            if (!stringValue(book.title)) return { book, field: 'title' };
            if (!stringValue(book.author)) return { book, field: 'author' };
            if (!book.grades.length) return { book, field: 'grades' };
        }
        return null;
    }

    async function writeFile(handle, contents) {
        const writable = await handle.createWritable();
        await writable.write(contents);
        await writable.close();
    }

    function downloadDataFile() {
        downloadBlob(serialiseData(), DATA_FILE, 'text/javascript;charset=utf-8');
    }

    function downloadPendingCovers() {
        let count = 0;
        for (const book of data) {
            const pending = pendingCovers.get(book);
            if (!pending) continue;
            const delay = 650 + count * 180;
            window.setTimeout(() => downloadBlob(pending.file, pending.fileName, pending.file.type), delay);
            count += 1;
        }
        return count;
    }

    function downloadBlob(contents, fileName, type) {
        const url = URL.createObjectURL(contents instanceof Blob ? contents : new Blob([contents], { type }));
        const link = document.createElement('a');
        link.href = url;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    }

    function makeCoverFileName(file) {
        const extension = (file.name.split('.').pop() || 'jpg').toLowerCase().replace(/[^a-z0-9]/g, '') || 'jpg';
        const base = stringValue(activeBook.title || file.name.replace(/\.[^.]+$/, ''))
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '_')
            .replace(/^_+|_+$/g, '') || 'boek';
        return `${base}.${extension}`;
    }

    function handleCoverUpload(file) {
        if (!activeBook || !file) return;
        const oldPending = pendingCovers.get(activeBook);
        if (oldPending) URL.revokeObjectURL(oldPending.previewUrl);
        const fileName = makeCoverFileName(file);
        const previewUrl = URL.createObjectURL(file);
        pendingCovers.set(activeBook, { file, fileName, previewUrl });
        activeBook.cover_front = `covers/${fileName}`;
        form.elements.cover_front.value = activeBook.cover_front;
        setDirty();
        updateCoverPreview();
        renderList();
    }

    function showToast(message, isError) {
        const toast = document.getElementById('toast');
        window.clearTimeout(toastTimer);
        toast.textContent = message;
        toast.classList.toggle('error', Boolean(isError));
        toast.classList.add('visible');
        toastTimer = window.setTimeout(() => toast.classList.remove('visible'), 4200);
    }

    document.querySelectorAll('.grade-tab').forEach((tab) => {
        tab.addEventListener('click', () => {
            activeGrade = tab.dataset.grade;
            document.querySelectorAll('.grade-tab').forEach((other) => other.classList.toggle('active', other === tab));
            search.value = '';
            renderList();
        });
    });

    form.addEventListener('input', (event) => {
        updateBookFromForm();
        if (event.target.name === 'synopsis') updateSynopsisCount();
        if (event.target.name === 'cover_front') updateCoverPreview();
        updateEditorHeading();
        setDirty();
        renderList();
    });

    form.addEventListener('submit', (event) => { event.preventDefault(); saveAll(); });
    search.addEventListener('input', renderList);
    document.getElementById('add-book').addEventListener('click', addBook);
    document.getElementById('delete-book').addEventListener('click', deleteBook);
    document.getElementById('folder-button').addEventListener('click', chooseProjectFolder);
    document.getElementById('side-folder-button').addEventListener('click', chooseProjectFolder);
    document.getElementById('save-button').addEventListener('click', saveAll);
    document.getElementById('cover-upload').addEventListener('change', (event) => {
        handleCoverUpload(event.target.files[0]);
        event.target.value = '';
    });
    coverImage.addEventListener('error', () => {
        coverImage.hidden = true;
        coverPlaceholder.hidden = false;
    });
    document.getElementById('notice-close').addEventListener('click', () => {
        document.getElementById('notice').remove();
    });
    window.addEventListener('beforeunload', (event) => {
        if (!isDirty) return;
        event.preventDefault();
        event.returnValue = '';
    });

    data = data.map(normaliseBook);
    renderList();
})();
