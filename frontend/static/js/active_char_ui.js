document.addEventListener('DOMContentLoaded', () => {
    // Carregar estilos básicos das cartas flutuantes
    const style = document.createElement('style');
    style.innerHTML = `
        #active-chars-container {
            position: fixed;
            bottom: 20px;
            right: 30px;
            display: flex;
            flex-direction: column;
            gap: 15px;
            z-index: 1000;
            max-height: 90vh;
            overflow-y: auto;
            overflow-x: hidden;
            padding-right: 15px; /* Compensa espaço barra rulagem pra não tampar card */
        }
        
        #active-chars-container::-webkit-scrollbar {
            width: 8px;
        }

        #active-chars-container::-webkit-scrollbar-track {
            background: rgba(0,0,0,0.2);
            border-radius: 4px;
        }

        #active-chars-container::-webkit-scrollbar-thumb {
            background: var(--gold-dark);
            border-radius: 4px;
        }
        
        .active-char-floating-card {
            display: flex;
            flex-direction: column;
            align-items: center;
            background: rgba(20, 20, 20, 0.9);
            border: 1px solid var(--gold-dim);
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.8);
            transition: height 0.3s ease, background 0.3s, border-color 0.3s;
            cursor: pointer;
            overflow: hidden;
            width: 140px; 
            height: 100px; /* Apenas a foto aparece por padrão */
            text-decoration: none;
            position: relative;
        }

        .active-char-floating-card:hover {
            height: 260px; /* Expandido para formato carta */
            background: rgba(30, 30, 30, 0.95);
            border-color: var(--gold);
        }

        .active-char-details {
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            width: 100%;
            height: 0px;
            padding: 0 8px;
            box-sizing: border-box;
            color: #fff;
            opacity: 0;
            transition: opacity 0.3s ease, height 0.3s ease, padding 0.3s ease;
            overflow: hidden;
        }

        .active-char-floating-card:hover .active-char-details {
            height: 160px;
            opacity: 1;
            padding: 8px;
        }
        
        .active-char-avatar, .active-char-avatar-placeholder {
            width: 100%;
            height: 100px;
            object-fit: cover;
            border-bottom: 1px solid var(--gold-dim);
            flex-shrink: 0;
        }
        
        .active-char-avatar-placeholder {
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(0,0,0,0.5);
        }

        .ac-name {
            font-family: 'Cinzel', serif;
            color: var(--gold);
            font-size: 1.1em;
            margin-bottom: 2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .ac-info {
            font-size: 0.8em;
            color: #aaa;
            margin-bottom: 8px;
        }

        .ac-bars {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .ac-bar-row {
            display: flex;
            align-items: center;
            font-size: 0.7em;
            font-weight: bold;
        }
        
        .ac-bar-label {
            width: 25px;
        }

        .ac-bar-track {
            flex-grow: 1;
            height: 6px;
            background: rgba(0,0,0,0.5);
            border-radius: 3px;
            overflow: hidden;
            margin-left: 5px;
        }

        .ac-bar-fill {
            height: 100%;
            border-radius: 3px;
            transition: width 0.3s;
        }
    `;
    document.head.appendChild(style);

    const container = document.createElement('div');
    container.id = 'active-chars-container';
    document.body.appendChild(container);

    fetch('/api/active_characters')
        .then(r => r.json())
        .then(data => {
            if (data.status === 'success' && data.data) {
                data.data.forEach(p => {
                    const card = document.createElement('a');
                    card.href = `/ficha/${p.id}`;
                    card.className = 'active-char-floating-card';

                    const pctPv = p.pv_max > 0 ? (p.pv_atual / p.pv_max * 100) : 0;
                    const pctPa = p.pa_max > 0 ? (p.pa_atual / p.pa_max * 100) : 0;
                    const pctPh = p.ph_max > 0 ? (p.ph_atual / p.ph_max * 100) : 0;
                    const pctPg = p.pg_max > 0 ? (p.pg_atual / p.pg_max * 100) : 0;

                    let avatarHtml = '';
                    if (p.avatar) {
                        avatarHtml = `<img src="${p.avatar}" class="active-char-avatar">`;
                    } else {
                        avatarHtml = `
                        <div class="active-char-avatar-placeholder">
                            <span class="material-icons" style="font-size: 3em; color: var(--gold-dim);">account_circle</span>
                        </div>
                    `;
                    }

                    card.innerHTML = `
                    ${avatarHtml}
                    <div class="active-char-details">
                        <div class="ac-name">${p.nome}</div>
                        <div class="ac-info">${p.jogador} | Nv ${p.nivel}</div>
                        <div class="ac-info" style="margin-top: -6px;">${p.classe} | ${p.raca}</div>
                        
                        <div class="ac-bars">
                            <div class="ac-bar-row">
                                <span class="ac-bar-label" style="color: #ef9a9a;">PV</span>
                                <div class="ac-bar-track"><div class="ac-bar-fill" style="width: ${pctPv}%; background: #b71c1c;"></div></div>
                            </div>
                            <div class="ac-bar-row">
                                <span class="ac-bar-label" style="color: #fff59d;">PA</span>
                                <div class="ac-bar-track"><div class="ac-bar-fill" style="width: ${pctPa}%; background: #f57f17;"></div></div>
                            </div>
                            <div class="ac-bar-row">
                                <span class="ac-bar-label" style="color: #90caf9;">PH</span>
                                <div class="ac-bar-track"><div class="ac-bar-fill" style="width: ${pctPh}%; background: #0d47a1;"></div></div>
                            </div>
                            <div class="ac-bar-row">
                                <span class="ac-bar-label" style="color: #e1bee7;">PG</span>
                                <div class="ac-bar-track"><div class="ac-bar-fill" style="width: ${pctPg}%; background: #7b1fa2;"></div></div>
                            </div>
                        </div>
                    </div>
                `;

                    container.appendChild(card);
                });
            }
        })
        .catch(e => console.error("Erro ao carregar fichas ativas:", e));
});
