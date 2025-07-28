class HakoiriPuzzleUI {
    constructor() {
        this.board = Array(5).fill(null).map(() => Array(4).fill(0));
        this.selectedShape = 'empty';
        this.currentStep = 0;
        this.totalSteps = 0;
        this.solutionAvailable = false;
        
        // ドラッグ&ドロップ用の状態
        this.draggedPieceId = null;
        this.draggedPieceOrigin = null;
        
        // 形状ベースの定義
        this.shapeDefinitions = {
            empty: { width: 1, height: 1, color: '#f8f9fa', maxCount: 999 },
            main: { width: 2, height: 2, color: '#FF6B6B', maxCount: 1 },
            horizontal: { width: 2, height: 1, color: '#4ECDC4', maxCount: 4 },
            vertical: { width: 1, height: 2, color: '#45B7D1', maxCount: 4 },
            square: { width: 1, height: 1, color: '#96CEB4', maxCount: 4 }
        };
        
        // 動的ID管理
        this.nextPieceIds = {
            main: 1,
            horizontal: 2,  // H1=2, H2=3, H3=4, H4=5
            vertical: 6,    // V1=6, V2=7, V3=8, V4=9
            square: 10      // S1=10, S2=11, S3=12, S4=13
        };
        
        // 既存のピースプロパティ（互換性のため）
        this.pieceProperties = {
            0: { width: 1, height: 1, name: '空', color: '#f8f9fa' },
            1: { width: 2, height: 2, name: 'MP', color: '#FF6B6B' },
            2: { width: 2, height: 1, name: 'H1', color: '#4ECDC4' },
            3: { width: 2, height: 1, name: 'H2', color: '#4ECDC4' },
            4: { width: 2, height: 1, name: 'H3', color: '#4ECDC4' },
            5: { width: 2, height: 1, name: 'H4', color: '#4ECDC4' },
            6: { width: 1, height: 2, name: 'V1', color: '#45B7D1' },
            7: { width: 1, height: 2, name: 'V2', color: '#45B7D1' },
            8: { width: 1, height: 2, name: 'V3', color: '#45B7D1' },
            9: { width: 1, height: 2, name: 'V4', color: '#45B7D1' },
            10: { width: 1, height: 1, name: 'S1', color: '#96CEB4' },
            11: { width: 1, height: 1, name: 'S2', color: '#96CEB4' },
            12: { width: 1, height: 1, name: 'S3', color: '#96CEB4' },
            13: { width: 1, height: 1, name: 'S4', color: '#96CEB4' }
        };
        
        this.init();
    }
    
    init() {
        console.log('HakoiriPuzzleUI init() started');
        try {
            this.createBoard();
            console.log('createBoard() completed');
            this.setupEventListeners();
            console.log('setupEventListeners() completed');
            this.loadDefaultBoard();
            console.log('loadDefaultBoard() completed');
        } catch (error) {
            console.error('Error in init():', error);
        }
    }
    
    createBoard() {
        const boardElement = document.getElementById('puzzle-board');
        boardElement.innerHTML = '';
        
        for (let row = 0; row < 5; row++) {
            for (let col = 0; col < 4; col++) {
                const cell = document.createElement('div');
                cell.className = 'board-cell';
                cell.dataset.row = row;
                cell.dataset.col = col;
                cell.addEventListener('click', (e) => this.handleCellClick(e));
                
                // ドラッグ&ドロップイベント
                cell.addEventListener('mousedown', (e) => this.handleMouseDown(e));
                cell.addEventListener('mouseover', (e) => this.handleMouseOver(e));
                cell.addEventListener('mouseup', (e) => this.handleMouseUp(e));
                
                boardElement.appendChild(cell);
            }
        }
        
        // 目標位置を示すマーカーを追加
        this.addGoalMarkers();
    }
    
    addGoalMarkers() {
        const boardElement = document.getElementById('puzzle-board');
        const goalRow = 3;
        const goalCols = [1, 2];
        
        goalCols.forEach(col => {
            for (let r = 0; r < 2; r++) {
                const cell = boardElement.children[(goalRow + r) * 4 + col];
                cell.classList.add('goal-cell');
            }
        });
    }
    
    setupEventListeners() {
        // ピース選択（形状ベース）
        const pieceItems = document.querySelectorAll('.piece-item');
        console.log('Found piece items:', pieceItems.length);
        
        pieceItems.forEach(item => {
            item.addEventListener('click', (e) => {
                const shape = item.dataset.shape;
                
                // 最大数チェック
                if (shape !== 'empty' && this.getShapeCount(shape) >= this.shapeDefinitions[shape].maxCount) {
                    this.showMessage(`${item.dataset.name}の最大配置数に達しています`, 'warning');
                    return;
                }
                
                document.querySelectorAll('.piece-item').forEach(p => p.classList.remove('selected'));
                item.classList.add('selected');
                this.selectedShape = shape;
            });
        });
        
        // コントロールボタン
        const resetButton = document.getElementById('reset-board');
        const solveButton = document.getElementById('solve-puzzle');
        
        console.log('Reset button found:', !!resetButton);
        console.log('Solve button found:', !!solveButton);
        
        if (resetButton) {
            resetButton.addEventListener('click', () => this.resetBoard());
        } else {
            console.error('reset-board button not found!');
        }
        
        if (solveButton) {
            solveButton.addEventListener('click', () => this.solvePuzzle());
        } else {
            console.error('solve-puzzle button not found!');
        }
        
        // 中止ボタンがあるかチェックして追加
        const stopButton = document.getElementById('stop-solving');
        if (stopButton) {
            stopButton.addEventListener('click', () => this.stopSolving());
        }
        
        // ステップコントロール（メイン）
        document.getElementById('next-step-main').addEventListener('click', () => this.nextStep());
        document.getElementById('prev-step-main').addEventListener('click', () => this.prevStep());
        
        // デフォルトで空が選択されている（HTMLで設定済み）
    }
    
    loadDefaultBoard() {
        // デフォルトの盤面を設定（確実に解ける標準配置・約30手）
        this.board = [
            [12, 4, 4, 13],  // S3, H3, H3, S4
            [6, 1, 1, 7],    // V1, MP, MP, V2
            [6, 1, 1, 7],    // V1, MP, MP, V2
            [10, 2, 2, 11],  // S1, H1, H1, S2
            [0, 3, 3, 0]     // EM, H2, H2, EM
        ];
        this.renderBoard();
    }
    
    handleCellClick(event) {
        if (this.solutionAvailable) {
            this.showMessage('解の表示中は盤面を編集できません', 'warning');
            return;
        }
        
        const row = parseInt(event.target.dataset.row);
        const col = parseInt(event.target.dataset.col);
        
        if (this.selectedShape === 'empty') {
            // 空のセルに設定（マルチセルピースの場合は全体を消去）
            this.clearPieceAt(row, col);
        } else {
            // ピースを配置
            this.placeShapePiece(row, col, this.selectedShape);
        }
        
        this.renderBoard();
    }
    
    handleMouseDown(event) {
        if (this.solutionAvailable) return; // 解の表示中はドラッグ無効
        
        const row = parseInt(event.target.dataset.row);
        const col = parseInt(event.target.dataset.col);
        const pieceId = this.board[row][col];
        
        if (pieceId === 0) return; // 空のセルはドラッグできない
        
        // ドラッグ開始
        this.draggedPieceId = pieceId;
        this.draggedPieceOrigin = { row, col };
        
        // ドラッグ中の視覚的フィードバック
        this.highlightDraggedPiece(pieceId, true);
        
        // マウスカーソルを変更
        document.body.style.cursor = 'grabbing';
        
        // ドラッグ中はクリックイベントを無効化
        event.preventDefault();
    }
    
    handleMouseOver(event) {
        if (!this.draggedPieceId) return;
        
        const row = parseInt(event.target.dataset.row);
        const col = parseInt(event.target.dataset.col);
        
        // ドロップ可能な位置かチェック
        if (this.canDropPieceAt(this.draggedPieceId, row, col)) {
            event.target.classList.add('drop-target');
            this.highlightDropZone(this.draggedPieceId, row, col, true);
        } else {
            this.clearDropHighlights();
        }
    }
    
    handleMouseUp(event) {
        if (!this.draggedPieceId) return;
        
        const row = parseInt(event.target.dataset.row);
        const col = parseInt(event.target.dataset.col);
        
        // ドロップ処理
        if (this.canDropPieceAt(this.draggedPieceId, row, col)) {
            this.movePiece(this.draggedPieceId, this.draggedPieceOrigin, { row, col });
        }
        
        // ドラッグ状態をリセット
        this.resetDragState();
    }
    
    highlightDraggedPiece(pieceId, highlight) {
        const cells = document.querySelectorAll('.board-cell');
        cells.forEach(cell => {
            const cellRow = parseInt(cell.dataset.row);
            const cellCol = parseInt(cell.dataset.col);
            if (this.board[cellRow][cellCol] === pieceId) {
                if (highlight) {
                    cell.classList.add('dragging');
                } else {
                    cell.classList.remove('dragging');
                }
            }
        });
    }
    
    highlightDropZone(pieceId, targetRow, targetCol, highlight) {
        const piece = this.pieceProperties[pieceId];
        if (!piece) return;
        
        const cells = document.querySelectorAll('.board-cell');
        cells.forEach(cell => {
            const cellRow = parseInt(cell.dataset.row);
            const cellCol = parseInt(cell.dataset.col);
            
            // ドロップ先の範囲内かチェック
            if (cellRow >= targetRow && cellRow < targetRow + piece.height &&
                cellCol >= targetCol && cellCol < targetCol + piece.width) {
                if (highlight) {
                    cell.classList.add('drop-zone');
                } else {
                    cell.classList.remove('drop-zone');
                }
            }
        });
    }
    
    clearDropHighlights() {
        const cells = document.querySelectorAll('.board-cell');
        cells.forEach(cell => {
            cell.classList.remove('drop-target', 'drop-zone');
        });
    }
    
    canDropPieceAt(pieceId, targetRow, targetCol) {
        const piece = this.pieceProperties[pieceId];
        if (!piece) return false;
        
        // 盤面外チェック
        if (targetRow + piece.height > 5 || targetCol + piece.width > 4) {
            return false;
        }
        
        // 衝突チェック（自分自身は除く）
        for (let r = targetRow; r < targetRow + piece.height; r++) {
            for (let c = targetCol; c < targetCol + piece.width; c++) {
                const cellValue = this.board[r][c];
                if (cellValue !== 0 && cellValue !== pieceId) {
                    return false;
                }
            }
        }
        
        return true;
    }
    
    movePiece(pieceId, fromPos, toPos) {
        // 元の位置をクリア
        this.clearExistingPiece(pieceId);
        
        // 新しい位置に配置
        const piece = this.pieceProperties[pieceId];
        for (let r = toPos.row; r < toPos.row + piece.height; r++) {
            for (let c = toPos.col; c < toPos.col + piece.width; c++) {
                this.board[r][c] = pieceId;
            }
        }
        
        this.renderBoard();
    }
    
    resetDragState() {
        this.highlightDraggedPiece(this.draggedPieceId, false);
        this.clearDropHighlights();
        this.draggedPieceId = null;
        this.draggedPieceOrigin = null;
        document.body.style.cursor = 'default';
    }
    
    clearExistingPiece(pieceId) {
        for (let row = 0; row < 5; row++) {
            for (let col = 0; col < 4; col++) {
                if (this.board[row][col] === pieceId) {
                    this.board[row][col] = 0;
                }
            }
        }
    }
    
    placePiece(row, col, pieceId) {
        const piece = this.pieceProperties[pieceId];
        if (!piece) return;
        
        // 配置可能かチェック
        if (row + piece.height > 5 || col + piece.width > 4) {
            this.showMessage('ピースが盤面からはみ出します', 'error');
            return;
        }
        
        // 同じピースIDが既に存在する場合は削除
        this.clearExistingPiece(pieceId);
        
        // 配置先に他のピースがある場合はエラー
        for (let r = row; r < row + piece.height; r++) {
            for (let c = col; c < col + piece.width; c++) {
                if (this.board[r][c] !== 0) {
                    this.showMessage('他のピースと重複しています', 'error');
                    return;
                }
            }
        }
        
        // ピースを配置
        for (let r = row; r < row + piece.height; r++) {
            for (let c = col; c < col + piece.width; c++) {
                this.board[r][c] = pieceId;
            }
        }
    }
    
    clearPieceAt(row, col) {
        const pieceId = this.board[row][col];
        if (pieceId !== 0) {
            this.clearExistingPiece(pieceId);
        }
    }
    
    placeShapePiece(row, col, shape) {
        if (shape === 'empty') return;
        
        const shapeInfo = this.shapeDefinitions[shape];
        if (!shapeInfo) return;
        
        // 配置可能かチェック
        if (row + shapeInfo.height > 5 || col + shapeInfo.width > 4) {
            this.showMessage(`${shape}が盤面からはみ出します`, 'error');
            return;
        }
        
        // 最大数チェック
        if (this.getShapeCount(shape) >= shapeInfo.maxCount) {
            this.showMessage(`${shape}の最大配置数に達しています`, 'warning');
            return;
        }
        
        // 配置先に他のピースがある場合はクリア
        for (let r = row; r < row + shapeInfo.height; r++) {
            for (let c = col; c < col + shapeInfo.width; c++) {
                const existingPieceId = this.board[r][c];
                if (existingPieceId !== 0) {
                    this.clearExistingPiece(existingPieceId);
                }
            }
        }
        
        // 新しいピースIDを取得
        const pieceId = this.getNextPieceId(shape);
        
        // ピースを配置
        for (let r = row; r < row + shapeInfo.height; r++) {
            for (let c = col; c < col + shapeInfo.width; c++) {
                this.board[r][c] = pieceId;
            }
        }
    }
    
    getNextPieceId(shape) {
        const nextId = this.nextPieceIds[shape];
        this.nextPieceIds[shape]++;
        return nextId;
    }
    
    getShapeCount(shape) {
        let count = 0;
        const shapeInfo = this.shapeDefinitions[shape];
        
        // 形状に対応するピースIDの範囲をチェック
        const usedIds = new Set();
        for (let row = 0; row < 5; row++) {
            for (let col = 0; col < 4; col++) {
                const pieceId = this.board[row][col];
                if (pieceId > 0) {
                    usedIds.add(pieceId);
                }
            }
        }
        
        // 形状別のカウント
        usedIds.forEach(id => {
            const piece = this.pieceProperties[id];
            if (piece) {
                if (shape === 'main' && id === 1) count++;
                else if (shape === 'horizontal' && id >= 2 && id <= 5) count++;
                else if (shape === 'vertical' && id >= 6 && id <= 9) count++;
                else if (shape === 'square' && id >= 10 && id <= 13) count++;
            }
        });
        
        return count;
    }
    
    renderBoard() {
        const cells = document.querySelectorAll('.board-cell');
        
        cells.forEach((cell, index) => {
            const row = Math.floor(index / 4);
            const col = index % 4;
            const pieceId = this.board[row][col];
            const piece = this.pieceProperties[pieceId];
            
            // クラスをリセット
            cell.className = 'board-cell';
            cell.style.background = '';
            cell.textContent = '';
            
            // 目標セルマーカーを再追加
            if ((row === 3 || row === 4) && (col === 1 || col === 2)) {
                cell.classList.add('goal-cell');
            }
            
            if (pieceId === 0) {
                cell.classList.add('empty');
            } else if (piece) {
                cell.classList.add('piece');
                cell.style.background = piece.color;
                
                // ピース名を表示（中央のセルのみ）
                if (this.isPieceCenterCell(row, col, pieceId)) {
                    cell.textContent = piece.name;
                    cell.classList.add('piece-center');
                    
                    if (pieceId === 1) { // MP
                        cell.classList.add('main-piece', 'large-piece');
                    }
                }
            }
        });
        
        // ピースカウントを更新
        this.updatePieceCounts();
    }
    
    isPieceCenterCell(row, col, pieceId) {
        const piece = this.pieceProperties[pieceId];
        if (!piece) return false;
        
        // ピースの左上位置を見つける
        let topRow = row, leftCol = col;
        for (let r = 0; r <= row; r++) {
            for (let c = 0; c <= col; c++) {
                if (this.board[r][c] === pieceId) {
                    topRow = Math.min(topRow, r);
                    leftCol = Math.min(leftCol, c);
                }
            }
        }
        
        // 中央位置を計算
        const centerRow = topRow + Math.floor(piece.height / 2);
        const centerCol = leftCol + Math.floor(piece.width / 2);
        
        return row === centerRow && col === centerCol;
    }
    
    updatePieceCounts() {
        // 各形状のカウントを更新
        const counts = {
            horizontal: this.getShapeCount('horizontal'),
            vertical: this.getShapeCount('vertical'),
            square: this.getShapeCount('square')
        };
        
        document.querySelectorAll('.piece-item').forEach(item => {
            const shape = item.dataset.shape;
            const countElement = item.querySelector('.piece-count');
            
            if (countElement && counts[shape] !== undefined) {
                const maxCount = this.shapeDefinitions[shape].maxCount;
                countElement.textContent = `${counts[shape]}/${maxCount}`;
                
                if (counts[shape] >= maxCount) {
                    item.classList.add('max-reached');
                } else {
                    item.classList.remove('max-reached');
                }
            }
        });
    }
    
    resetBoard() {
        console.log('resetBoard() called');
        
        // 選択を空に戻す
        document.querySelectorAll('.piece-item').forEach(p => p.classList.remove('selected'));
        document.querySelector('.piece-item[data-shape="empty"]').classList.add('selected');
        this.selectedShape = 'empty';
        
        this.currentStep = 0;
        this.totalSteps = 0;
        this.solutionAvailable = false;
        
        // ピースIDカウンターをリセット
        this.nextPieceIds = {
            main: 1,
            horizontal: 2,
            vertical: 6,
            square: 10
        };
        
        // デフォルトの盤面を再設定
        this.loadDefaultBoard();
        this.hideStepControls();
        this.clearMessage();
    }
    
    async solvePuzzle() {
        console.log('solvePuzzle() started');
        this.startProgressIndicator();
        
        try {
            // 盤面の初期化
            console.log('Sending initialize request...');
            const initResponse = await fetch('/api/initialize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ board: this.board }),
                credentials: 'same-origin'
            });
            const initData = await initResponse.json();
            console.log('Initialize response:', initData);
            
            if (!initData.success) {
                this.stopProgressIndicator();
                this.showMessage('初期化に失敗しました: ' + initData.error + ' [クリックで閉じる]', 'error', false);
                return;
            }
            
            // パズルを解く（バックグラウンド処理開始）
            console.log('Sending solve request...');
            const solveResponse = await fetch('/api/solve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin'
            });
            const solveData = await solveResponse.json();
            console.log('Solve response:', solveData);
            
            if (solveData.success) {
                console.log('Starting real-time progress...');
                console.log('Session ID:', solveData.session_id);
                this.sessionId = solveData.session_id;
                // リアルタイム進捗表示開始
                this.startRealTimeProgress();
            } else {
                console.error('Solve failed:', solveData.error);
                this.stopProgressIndicator();
                this.showMessage('解決開始に失敗しました: ' + solveData.error + ' [クリックで閉じる]', 'error', false);
            }
            
        } catch (error) {
            this.stopProgressIndicator();
            this.showMessage('エラーが発生しました: ' + error.message + ' [クリックで閉じる]', 'error', false);
        }
    }
    
    async stopSolving() {
        try {
            // 中止リクエスト送信
            const response = await fetch('/api/stop', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                // EventSourceを閉じる
                if (this.progressEventSource) {
                    this.progressEventSource.close();
                    this.progressEventSource = null;
                }
                
                this.stopProgressIndicator();
                this.showMessage('探索を中止しました', 'warning');
            }
        } catch (error) {
            console.error('中止エラー:', error);
            this.showMessage('中止処理でエラーが発生しました', 'error');
        }
    }
    
    startRealTimeProgress() {
        console.log('startRealTimeProgress() called');
        if (this.progressEventSource) {
            console.log('Closing existing EventSource');
            this.progressEventSource.close();
        }
        
        // Server-Sent Eventsで進捗を受信
        const progressUrl = `/api/progress?session_id=${this.sessionId}`;
        console.log('Creating new EventSource for:', progressUrl);
        this.progressEventSource = new EventSource(progressUrl, {
            withCredentials: true
        });
        
        this.progressEventSource.onopen = (event) => {
            console.log('EventSource opened:', event);
        };
        
        this.progressEventSource.onmessage = (event) => {
            console.log('EventSource message received:', event.data);
            try {
                const data = JSON.parse(event.data);
                console.log('Parsed progress data:', data);
                this.handleProgressUpdate(data);
            } catch (error) {
                console.error('進捗データのパースエラー:', error);
            }
        };
        
        this.progressEventSource.onerror = (error) => {
            console.error('進捗受信エラー:', error);
            console.log('EventSource readyState:', this.progressEventSource.readyState);
            this.progressEventSource.close();
            this.progressEventSource = null;
        };
    }
    
    handleProgressUpdate(data) {
        if (data.type === 'progress') {
            // 進捗更新
            this.updateRealTimeProgress(data);
        } else if (data.type === 'final_result') {
            // 最終結果
            this.handleFinalResult(data);
        } else if (data.type === 'heartbeat') {
            // ハートビート（何もしない）
        } else if (data.error) {
            this.stopProgressIndicator();
            this.showMessage('進捗取得エラー: ' + data.error, 'error', false);
        }
    }
    
    updateRealTimeProgress(data) {
        // 探索件数を更新（重複チェック）
        const exploredCountElement = document.getElementById('explored-count');
        if (exploredCountElement) {
            const countText = `${data.explored_count.toLocaleString()}`;
            if (exploredCountElement.textContent !== countText) {
                exploredCountElement.classList.add('updating');
                exploredCountElement.textContent = countText;
                setTimeout(() => exploredCountElement.classList.remove('updating'), 300);
            }
        }
        
        // 現在手数を更新（重複チェック）
        const currentMovesElement = document.getElementById('current-moves');
        if (currentMovesElement) {
            const movesText = `${data.current_moves}`;
            if (currentMovesElement.textContent !== movesText) {
                currentMovesElement.classList.add('updating');
                currentMovesElement.textContent = movesText;
                setTimeout(() => currentMovesElement.classList.remove('updating'), 300);
            }
        }
        
        // 推定残り手数を更新（重複チェック）
        const estimatedRemainingElement = document.getElementById('estimated-remaining');
        if (estimatedRemainingElement) {
            const remainingText = `${data.estimated_remaining}`;
            if (estimatedRemainingElement.textContent !== remainingText) {
                estimatedRemainingElement.classList.add('updating');
                estimatedRemainingElement.textContent = remainingText;
                setTimeout(() => estimatedRemainingElement.classList.remove('updating'), 300);
            }
        }
        
        // 経過時間を更新
        this.updateElapsedTime();
    }
    
    handleFinalResult(data) {
        // EventSourceを閉じる
        if (this.progressEventSource) {
            this.progressEventSource.close();
            this.progressEventSource = null;
        }
        
        this.stopProgressIndicator();
        
        if (data.success) {
            this.totalSteps = data.total_steps;
            this.currentStep = 0;
            this.solutionAvailable = true;
            
            // ステップコントロールを表示
            this.showStepControls();
            
            // 最初のステップを表示
            this.displayStep(0);
            
            this.showMessage(`解決しました！手数: ${data.total_steps} [クリックで閉じる]`, 'success', false);
            this.triggerCelebration();
        } else {
            this.showMessage('解が見つかりませんでした [クリックで閉じる]', 'error', false);
        }
    }
    
    startProgressIndicator() {
        // 進捗表示を開始
        const progressText = document.getElementById('progress-text');
        const progressTitle = document.getElementById('progress-title');
        const solveButton = document.getElementById('solve-puzzle');
        const stopButton = document.getElementById('stop-solving');
        
        if (progressText) progressText.style.display = 'block';
        if (progressTitle) progressTitle.textContent = '探索中...';
        if (solveButton) {
            solveButton.style.display = 'none';
        }
        if (stopButton) {
            stopButton.style.display = 'inline-block';
        }
        
        // 統計値をリセット
        this.resetProgressStats();
        
        // 開始時間を記録
        this.startTime = Date.now();
        this.progressTimer = setInterval(() => this.updateElapsedTime(), 1000);
    }
    
    stopProgressIndicator() {
        const progressText = document.getElementById('progress-text');
        const progressTitle = document.getElementById('progress-title');
        const solveButton = document.getElementById('solve-puzzle');
        const stopButton = document.getElementById('stop-solving');
        
        if (progressText) progressText.style.display = 'none';
        if (progressTitle) progressTitle.textContent = 'パズル操作';
        if (solveButton) {
            solveButton.style.display = 'inline-block';
        }
        if (stopButton) {
            stopButton.style.display = 'none';
        }
        
        if (this.progressTimer) {
            clearInterval(this.progressTimer);
            this.progressTimer = null;
        }
    }
    
    resetProgressStats() {
        const stats = ['explored-count', 'current-moves', 'estimated-remaining', 'elapsed-time'];
        stats.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.textContent = '-';
        });
    }
    
    updateElapsedTime() {
        if (!this.startTime) return;
        
        const elapsed = Date.now() - this.startTime;
        const seconds = Math.floor(elapsed / 1000);
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        
        const timeText = `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
        const elapsedTimeElement = document.getElementById('elapsed-time');
        if (elapsedTimeElement) {
            elapsedTimeElement.textContent = timeText;
        }
    }
    
    async nextStep() {
        if (!this.solutionAvailable) return;
        
        if (this.currentStep < this.totalSteps) {
            this.currentStep++;
            await this.displayStep(this.currentStep);
        } else {
            this.showMessage('最終ステップに到達しています', 'info');
        }
    }
    
    async prevStep() {
        if (!this.solutionAvailable) return;
        
        if (this.currentStep > 0) {
            this.currentStep--;
            await this.displayStep(this.currentStep);
        } else {
            this.showMessage('初期ステップです', 'info');
        }
    }
    
    async displayStep(step) {
        try {
            const response = await fetch(`/api/get_step/${step}`, {
                credentials: 'same-origin'
            });
            const data = await response.json();
            
            if (data.success) {
                this.board = data.board;
                this.renderBoard();
                
                // ステップ情報を更新
                this.updateStepInfo(step, data.total_steps, data.move);
            } else {
                this.showMessage('ステップの取得に失敗しました: ' + data.error, 'error');
            }
        } catch (error) {
            this.showMessage('エラーが発生しました: ' + error.message, 'error');
        }
    }
    
    updateStepInfo(currentStep, totalSteps, move) {
        const stepCounter = document.getElementById('step-counter-main');
        const moveDescription = document.getElementById('move-description-main');
        
        if (stepCounter) {
            stepCounter.textContent = `ステップ: ${currentStep} / ${totalSteps}`;
        }
        
        if (moveDescription) {
            if (currentStep === 0) {
                moveDescription.textContent = '初期状態';
            } else {
                moveDescription.textContent = move || '移動情報なし';
            }
        }
    }
    
    showStepControls() {
        const stepControls = document.getElementById('step-controls-main');
        if (stepControls) {
            stepControls.style.display = 'block';
        }
    }
    
    hideStepControls() {
        const stepControls = document.getElementById('step-controls-main');
        if (stepControls) {
            stepControls.style.display = 'none';
        }
    }
    
    showMessage(message, type = 'info', autoHide = true) {
        const statusElement = document.getElementById('status-message');
        if (!statusElement) return;
        
        statusElement.textContent = message;
        statusElement.className = `status-message ${type}`;
        statusElement.style.display = 'block';
        
        // クリックで閉じる機能
        if (!autoHide) {
            statusElement.style.cursor = 'pointer';
            statusElement.onclick = () => this.clearMessage();
        } else {
            statusElement.style.cursor = 'default';
            statusElement.onclick = null;
        }
        
        if (autoHide) {
            setTimeout(() => this.clearMessage(), 3000);
        }
    }
    
    clearMessage() {
        const statusElement = document.getElementById('status-message');
        if (statusElement) {
            statusElement.style.display = 'none';
            statusElement.onclick = null;
        }
    }
    
    triggerCelebration() {
        // 紙吹雪エフェクト
        this.createConfetti();
        
        // 成功音やアニメーションを追加する場合はここに
    }
    
    createConfetti() {
        const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57'];
        const confettiContainer = document.createElement('div');
        confettiContainer.className = 'celebration-container';
        document.body.appendChild(confettiContainer);
        
        for (let i = 0; i < 50; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.width = confetti.style.height = Math.random() * 10 + 5 + 'px';
            confetti.style.position = 'absolute';
            confetti.style.animation = `confetti-fall ${Math.random() * 3 + 2}s linear forwards`;
            
            confettiContainer.appendChild(confetti);
        }
        
        // 5秒後に削除
        setTimeout(() => {
            if (confettiContainer.parentNode) {
                confettiContainer.parentNode.removeChild(confettiContainer);
            }
        }, 5000);
    }
}

// パズルUIを初期化
document.addEventListener('DOMContentLoaded', () => {
    new HakoiriPuzzleUI();
});