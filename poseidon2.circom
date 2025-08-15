pragma circom 2.2.2;

// 修改SBox实现：使用不同的中间步骤计算x^5
template SBox() {
    signal input in_val;
    signal output out_val;
    
    // 先计算x^2和x^4
    signal val_sq;
    signal val_quad;
    val_sq <== in_val * in_val;
    val_quad <== val_sq * val_sq;
    out_val <== val_quad * in_val;  // x^5 = x^4 * x
}

// 优化轮次实现
template Poseidon2Round(round_type, round_idx, state_width) {
    signal input prev_state[state_width];
    signal output next_state[state_width];
    
    // MDS矩阵（值不变，表示方式改变）
    var mds[3][3] = [
        [2, 1, 1],
        [1, 2, 1],
        [1, 1, 2]
    ];
    
    // 更高效的轮常数生成
    var rc[64][3];
    for (var r = 0; r < 64; r++) {
        rc[r][0] = r*3 + 1;
        rc[r][1] = r*3 + 2;
        rc[r][2] = r*3 + 3;
    }
    
    // 添加轮常数
    signal intermediate[state_width];
    for (var i = 0; i < state_width; i++) {
        intermediate[i] <== prev_state[i] + rc[round_idx][i];
    }
    
    // 应用S-box
    signal post_sbox[state_width];
    component sboxes[state_width];
    
    if (round_type == 0) {  // 全轮次
        for (var i = 0; i < state_width; i++) {
            sboxes[i] = SBox();
            sboxes[i].in_val <== intermediate[i];
            post_sbox[i] <== sboxes[i].out_val;
        }
    } else {  // 部分轮次
        sboxes[0] = SBox();
        sboxes[0].in_val <== intermediate[0];
        post_sbox[0] <== sboxes[0].out_val;
        
        for (var i = 1; i < state_width; i++) {
            post_sbox[i] <== intermediate[i];
        }
    }
    
    // MDS混合
    for (var i = 0; i < state_width; i++) {
        next_state[i] <== mds[i][0]*post_sbox[0] + 
                         mds[i][1]*post_sbox[1] + 
                         mds[i][2]*post_sbox[2];
    }
}

template Poseidon2Hash() {
    var RF = 8;      // 全轮次数
    var RP = 56;     // 部分轮次数
    var TOTAL = RF + RP;
    var WIDTH = 3;
    
    signal input input_message[2];  // 两个输入元素
    signal input expected_output;
    
    // 状态历史记录
    signal state[TOTAL + 1][WIDTH];
    
    // 初始化状态（方式改变）
    state[0][0] <== input_message[0];
    state[0][1] <== input_message[1];
    state[0][2] <== 0;
    
    component rounds[TOTAL];
    
    for (var r = 0; r < TOTAL; r++) {
        // 优化轮次类型判断
        var is_full_round = 0;
        if (r < RF / 2 || r >= TOTAL - RF / 2) {
            is_full_round = 1;
        }
        
        rounds[r] = Poseidon2Round(is_full_round, r, WIDTH);
        
        for (var i = 0; i < WIDTH; i++) {
            rounds[r].prev_state[i] <== state[r][i];
            state[r + 1][i] <== rounds[r].next_state[i];
        }
    }
    
    // 输出约束（更直接的约束）
    expected_output === state[TOTAL][0];
}

component main = Poseidon2Hash();