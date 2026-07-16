# Quantum States

## North Pole (+Z)
**State:** $\vert0\rangle$  
**Description:** Standard classical 0 state with a 100% measurement probability.

## South Pole (-Z)
**State:** $\vert1\rangle$  
**Description:** Standard classical 1 state with a 100% measurement probability.

## Front Equator (+X)
**State:** $\vert+\rangle = \frac{1}{\sqrt{2}}(\vert0\rangle + \vert1\rangle)$  
**Description:** Equal superposition with a phase of 0.

## Back Equator (-X)
**State:** $\vert-\rangle = \frac{1}{\sqrt{2}}(\vert0\rangle - \vert1\rangle)$  
**Description:** Equal superposition with a phase of π (180°).

## Right Equator (+Y)
**State:** $\vert i\rangle = \frac{1}{\sqrt{2}}(\vert0\rangle + i\vert1\rangle)$  
**Description:** Equal superposition with an imaginary phase of π/2 (90°).

## Left Equator (-Y)
**State:** $\vert -i\rangle = \frac{1}{\sqrt{2}}(\vert0\rangle - i\vert1\rangle)$  
**Description:** Equal superposition with an imaginary phase of 3π/2 (270°).

# Quantum Gates

## 1. SX Gate (Square Root of X)
**Matrix:**  
$$\frac{1}{\sqrt{2}} \begin{pmatrix} 1 & -i \\ -i & 1 \end{pmatrix}$$

**Rotation:** $\frac{\pi}{2}$ rad (90°) over X-axis

## 2. SY Gate (Square Root of Y)
**Matrix:**  
$$\frac{1}{\sqrt{2}} \begin{pmatrix} 1 & -1 \\ 1 & 1 \end{pmatrix}$$

**Rotation:** $\frac{\pi}{2}$ rad (90°) over Y-axis

## 3. S Gate (SZ) — Phase Gate (Square Root of Z)
**Matrix:**  
$$\begin{pmatrix} 1 & 0 \\ 0 & i \end{pmatrix}$$

**Rotation:** $\frac{\pi}{2}$ rad (90°) over Z-axis

## 4. H Gate (Hadamard)
**Matrix:**  
$$\frac{1}{\sqrt{2}} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}$$

**Rotation:** $\pi$ rad (180°) over diagonal X+Z axis

## 5. X Gate (Pauli-X / NOT / Bit-Flip)
**Matrix:**  
$$\begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}$$

**Rotation:** $\pi$ rad (180°) over X-axis

## 6. Y Gate (Pauli-Y / Bit and Phase-Flip)
**Matrix:**  
$$\begin{pmatrix} 0 & -i \\ i & 0 \end{pmatrix}$$

**Rotation:** $\pi$ rad (180°) over Y-axis

## 7. Z Gate (Pauli-Z / Phase-Flip)
**Matrix:**  
$$\begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}$$

**Rotation:** $\pi$ rad (180°) over Z-axis