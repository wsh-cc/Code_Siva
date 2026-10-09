#include <stdio.h>
#include <stdint.h>

#define SIZE 65536

// 模拟一个64KB数据段
uint8_t memory[SIZE];

int main() {
    uint16_t BX = 0x0100;
    uint16_t SI = 0x0020;
    uint8_t AL = 0x5A;

    // 初始化存储器
    memory[0x0300] = 0x11;
    memory[BX] = 0x22;
    memory[SI] = 0x33;
    memory[BX + SI] = 0x44;
    memory[BX + SI + 0x10] = 0x55;
    memory[BX + SI * 2 + 0x10] = 0x66;

    // 1. 立即数寻址
    printf("立即数寻址: %02XH\n", 0x78);

    // 2. 寄存器寻址
    printf("寄存器寻址: %02XH\n", AL);

    // 3. 直接寻址
    printf("直接寻址: %02XH\n",
           memory[0x0300]);

    // 4. 寄存器间接寻址
    printf("寄存器间接寻址: %02XH\n",
           memory[BX]);

    // 5. 变址寻址
    printf("变址寻址: %02XH\n",
           memory[SI]);

    // 6. 基址变址寻址
    printf("基址变址寻址: %02XH\n",
           memory[BX + SI]);

    // 7. 相对基址变址寻址
    printf("相对基址变址寻址: %02XH\n",
           memory[BX + SI + 0x10]);

    // 8. 比例变址寻址（80386及以后）
    uint32_t EBX = BX;
    uint32_t ESI = SI;

    printf("比例变址寻址: %02XH\n",
           memory[EBX + ESI * 2 + 0x10]);

    return 0;
}