#include <stdio.h>
#include <stdint.h>
#include <string.h>
#define MEM_SIZE (1 << 20)

// 模拟1MB存储器
uint8_t memory[MEM_SIZE];

// 计算20位物理地址
uint32_t address(uint16_t seg, uint16_t off) {
    return (((uint32_t)seg << 4) + off) & 0xFFFFF;
}

// 写入一个字节
void write8(uint16_t seg, uint16_t off, uint8_t value) {
    memory[address(seg, off)] = value;
}

// 读取一个字节
uint8_t read8(uint16_t seg, uint16_t off) {
    return memory[address(seg, off)];
}

// 写入一个字（16位，小端存储）
void write16(uint16_t seg, uint16_t off, uint16_t value) {
    write8(seg, off, value & 0xFF);
    write8(seg, (uint16_t)(off + 1), value >> 8);
}

// 读取一个字
uint16_t read16(uint16_t seg, uint16_t off) {
    uint16_t low = read8(seg, off);
    uint16_t high = read8(seg, (uint16_t)(off + 1));
    return low | (high << 8);
}

int main() {
    uint16_t DS = 0x1000;
    uint16_t SS = 0x2000;
    uint16_t AX = 0x1234;
    uint16_t BX = 0;
    uint16_t SP = 0xFFFE;

    // 模拟 MOV [0100H], AX
    write16(DS, 0x0100, AX);

    // 模拟 MOV BX, [0100H]
    BX = read16(DS, 0x0100);

    printf("AX = %04XH\n", AX);
    printf("BX = %04XH\n", BX);

    printf("低字节 = %02XH\n", read8(DS, 0x0100));
    printf("高字节 = %02XH\n", read8(DS, 0x0101));

    // 模拟字节存储
    write8(DS, 0x0200, 0x5A);
    printf("字节读取 = %02XH\n", read8(DS, 0x0200));

    // 模拟 PUSH AX
    SP -= 2;
    write16(SS, SP, AX);
    printf("PUSH后 SP = %04XH\n", SP);

    // 模拟 POP AX
    AX = 0;
    AX = read16(SS, SP);
    SP += 2;

    printf("POP后 AX = %04XH\n", AX);
    printf("POP后 SP = %04XH\n", SP);

    return 0;
}