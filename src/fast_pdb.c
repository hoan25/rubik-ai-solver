#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

#define PDB_SIZE 88179840

static uint8_t pdb[PDB_SIZE];
static uint32_t queue[PDB_SIZE];

// Bảng dịch chuyển 18 nước đi cho góc
static uint8_t corner_map[18][8];
static uint8_t corner_delta[18][8];

static inline uint32_t encode_corners(const uint8_t cp[8], const uint8_t co[8]) {
    uint32_t c0 = (cp[1]<cp[0]) + (cp[2]<cp[0]) + (cp[3]<cp[0]) + (cp[4]<cp[0]) + (cp[5]<cp[0]) + (cp[6]<cp[0]) + (cp[7]<cp[0]);
    uint32_t c1 = (cp[2]<cp[1]) + (cp[3]<cp[1]) + (cp[4]<cp[1]) + (cp[5]<cp[1]) + (cp[6]<cp[1]) + (cp[7]<cp[1]);
    uint32_t c2 = (cp[3]<cp[2]) + (cp[4]<cp[2]) + (cp[5]<cp[2]) + (cp[6]<cp[2]) + (cp[7]<cp[2]);
    uint32_t c3 = (cp[4]<cp[3]) + (cp[5]<cp[3]) + (cp[6]<cp[3]) + (cp[7]<cp[3]);
    uint32_t c4 = (cp[5]<cp[4]) + (cp[6]<cp[4]) + (cp[7]<cp[4]);
    uint32_t c5 = (cp[6]<cp[5]) + (cp[7]<cp[5]);
    uint32_t c6 = (cp[7]<cp[6]);

    uint32_t perm_idx = c0 * 5040 + c1 * 720 + c2 * 120 + c3 * 24 + c4 * 6 + c5 * 2 + c6;
    uint32_t orient_idx = (((((co[0]*3 + co[1])*3 + co[2])*3 + co[3])*3 + co[4])*3 + co[5])*3 + co[6];

    return perm_idx * 2187 + orient_idx;
}

static inline void decode_corners(uint32_t idx, uint8_t cp[8], uint8_t co[8]) {
    uint32_t orient_idx = idx % 2187;
    uint32_t perm_idx = idx / 2187;

    for (int i = 6; i >= 0; i--) {
        co[i] = orient_idx % 3;
        orient_idx /= 3;
    }
    uint32_t sum_co = 0;
    for (int i = 0; i < 7; i++) sum_co += co[i];
    co[7] = (3 - (sum_co % 3)) % 3;

    static const int fact[8] = {5040, 720, 120, 24, 6, 2, 1, 1};
    uint8_t avail[8] = {0, 1, 2, 3, 4, 5, 6, 7};
    for (int i = 0; i < 7; i++) {
        int code = perm_idx / fact[i];
        perm_idx %= fact[i];
        cp[i] = avail[code];
        for (int j = code; j < 7 - i; j++) {
            avail[j] = avail[j + 1];
        }
    }
    cp[7] = avail[0];
}

void set_move_tables(const uint8_t maps[18][8], const uint8_t deltas[18][8]) {
    memcpy(corner_map, maps, sizeof(corner_map));
    memcpy(corner_delta, deltas, sizeof(corner_delta));
}

int build_c_pdb(uint8_t* out_pdb) {
    memset(pdb, 255, PDB_SIZE);

    uint8_t start_cp[8] = {0,1,2,3,4,5,6,7};
    uint8_t start_co[8] = {0,0,0,0,0,0,0,0};
    uint32_t start_idx = encode_corners(start_cp, start_co);
    pdb[start_idx] = 0;

    queue[0] = start_idx;
    uint32_t head = 0;
    uint32_t tail = 1;

    uint8_t cp[8], co[8];
    uint8_t new_cp[8], new_co[8];

    while (head < tail) {
        uint32_t curr_idx = queue[head++];
        uint8_t curr_depth = pdb[curr_idx];
        uint8_t next_depth = curr_depth + 1;

        decode_corners(curr_idx, cp, co);

        for (int m = 0; m < 18; m++) {
            const uint8_t* cmap = corner_map[m];
            const uint8_t* cdelta = corner_delta[m];

            for (int i = 0; i < 8; i++) {
                uint8_t src = cmap[i];
                new_cp[i] = cp[src];
                new_co[i] = (co[src] + cdelta[i]) % 3;
            }

            uint32_t next_idx = encode_corners(new_cp, new_co);
            if (pdb[next_idx] == 255) {
                pdb[next_idx] = next_depth;
                queue[tail++] = next_idx;
            }
        }
    }

    memcpy(out_pdb, pdb, PDB_SIZE);
    return tail;
}
