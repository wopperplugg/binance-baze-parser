export function renderOrderBook(containerId, orderBookData) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Контейнер с ID '${containerId}' не найден.`);
        return;
    }

    // Проверяем структуру данных
    if (!orderBookData || !Array.isArray(orderBookData.bids) || !Array.isArray(orderBookData.asks)) {
        container.innerHTML = '<p class="text-muted text-center">Некорректные данные стакана.</p>';
        return;
    }

    // Преобразуем строки в числа для удобства
    const bids = orderBookData.bids.map(([price, amount]) => [Number(price), Number(amount)]);
    const asks = orderBookData.asks.map(([price, amount]) => [Number(price), Number(amount)]);

    // Очищаем контейнер
    container.innerHTML = '';

    // Создаем обертку
    const wrapper = document.createElement('div');
    wrapper.classList.add('order-book-container-wrapper');

    // Заголовок
    const header = document.createElement('div');
    header.classList.add('order-book-header', 'd-flex', 'justify-content-between', 'fw-bold', 'pb-1', 'border-bottom');
    header.innerHTML = `
        <span>Цена</span>
        <span>Объем</span>
        <span>Всего</span>
    `;
    wrapper.appendChild(header);

    // Отрисовка ask (продажи) - отсортированы по возрастанию цены
    const asksContainer = document.createElement('div');
    asksContainer.classList.add('order-book-asks');

    // Проверяем, что asks — массив, и реверсируем его для отображения сверху вниз
    if (Array.isArray(asks)) {
        asks.slice().reverse().forEach(([price, amount]) => {
            const row = document.createElement('div');
            row.classList.add('order-book-row', 'd-flex', 'justify-content-between', 'py-1', 'text-danger');
            row.innerHTML = `
                <span>${price.toFixed(2)}</span>
                <span>${amount.toFixed(6)}</span>
                <span>${(price * amount).toFixed(2)}</span>
            `;
            asksContainer.appendChild(row);
        });
    } else {
        asksContainer.innerHTML = '<div class="text-muted p-2">Нет данных продаж</div>';
    }

    wrapper.appendChild(asksContainer);

    // Средняя цена (spread)
    const spreadContainer = document.createElement('div');
    spreadContainer.classList.add('spread', 'text-center', 'my-2', 'text-muted', 'fst-italic');
    if (bids.length > 0 && asks.length > 0) {
        const bestBid = bids[0][0];
        const bestAsk = asks[0][0];
        const midPrice = ((bestBid + bestAsk) / 2).toFixed(2);
        const spreadPercent = (((bestAsk - bestBid) / bestBid) * 100).toFixed(2);
        spreadContainer.textContent = `Средняя цена: ${midPrice} (Spread: ${spreadPercent}%)`;
    } else {
        spreadContainer.textContent = 'Нет данных для расчета средней цены';
    }
    wrapper.appendChild(spreadContainer);

    // Отрисовка bid (покупки) - отсортированы по убыванию цены
    const bidsContainer = document.createElement('div');
    bidsContainer.classList.add('order-book-bids');

    if (Array.isArray(bids)) {
        bids.forEach(([price, amount]) => {
            const row = document.createElement('div');
            row.classList.add('order-book-row', 'd-flex', 'justify-content-between', 'py-1', 'text-success');
            row.innerHTML = `
                <span>${price.toFixed(2)}</span>
                <span>${amount.toFixed(6)}</span>
                <span>${(price * amount).toFixed(2)}</span>
            `;
            bidsContainer.appendChild(row);
        });
    } else {
        bidsContainer.innerHTML = '<div class="text-muted p-2">Нет данных покупок</div>';
    }

    wrapper.appendChild(bidsContainer);

    // Добавляем обертку в контейнер
    container.appendChild(wrapper);
}