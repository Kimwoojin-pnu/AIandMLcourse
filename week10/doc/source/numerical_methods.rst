수치 해석 방법
==============

Week 10 코드에서 사용하는 핵심 수치 해석 기법을 정리합니다.

FDTD (Finite Difference Time Domain)
--------------------------------------

중앙 차분법
^^^^^^^^^^^

시간과 공간을 격자로 이산화하는 2차 정확도 방법:

.. math::

   \frac{\partial^2 u}{\partial t^2} \approx \frac{u^{n+1} - 2u^n + u^{n-1}}{\Delta t^2}

.. math::

   \frac{\partial^2 u}{\partial x^2} \approx \frac{u_{i+1} - 2u_i + u_{i-1}}{\Delta x^2}

CFL 안정성 조건
^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 20 35 45

   * - 차원
     - 조건
     - 설명
   * - 1D
     - :math:`c\Delta t/\Delta x \leq 1`
     - 광속 × 시간 스텝 ≤ 격자 간격
   * - 2D
     - :math:`c\Delta t\sqrt{1/\Delta x^2 + 1/\Delta y^2} \leq 1`
     - 2D에서 더 엄격 (대각 전파 고려)
   * - 3D
     - :math:`c\Delta t\sqrt{1/\Delta x^2 + 1/\Delta y^2 + 1/\Delta z^2} \leq 1`
     - 3D 최대 엄격

경계 조건 종류
^^^^^^^^^^^^^^

- **반사 경계**: :math:`E = 0` (도체 벽, 파동 반사)
- **흡수 경계 (PML)**: 파동을 흡수 (열린 공간 시뮬레이션)
- **주기 경계**: 한쪽 끝이 반대쪽 끝과 연결

Runge-Kutta 4차 방법 (RK4)
----------------------------

운동 방정식의 수치 적분. Euler 방법보다 정확도가 크게 향상됩니다:

.. math::

   k_1 = f(y_n, t_n)

.. math::

   k_2 = f\!\left(y_n + \tfrac{\Delta t}{2}k_1,\; t_n + \tfrac{\Delta t}{2}\right)

.. math::

   k_3 = f\!\left(y_n + \tfrac{\Delta t}{2}k_2,\; t_n + \tfrac{\Delta t}{2}\right)

.. math::

   k_4 = f\!\left(y_n + \Delta t\, k_3,\; t_n + \Delta t\right)

.. math::

   y_{n+1} = y_n + \frac{\Delta t}{6}(k_1 + 2k_2 + 2k_3 + k_4)

오차: :math:`O(\Delta t^4)` (Euler의 :math:`O(\Delta t)` 대비 훨씬 정확)

반복법 (Laplace Solver)
-----------------------

Jacobi 방법
^^^^^^^^^^^

모든 점을 동시에 업데이트 (이전 값 사용):

.. math::

   V_{i,j}^{(k+1)} = \frac{1}{4}\left(V_{i+1,j}^{(k)} + V_{i-1,j}^{(k)} + V_{i,j+1}^{(k)} + V_{i,j-1}^{(k)}\right)

Gauss-Seidel 방법
^^^^^^^^^^^^^^^^^

업데이트 즉시 새 값 사용 (약 2배 빠른 수렴):

.. math::

   V_{i,j}^{(k+1)} = \frac{1}{4}\left(V_{i+1,j}^{(k)} + V_{i-1,j}^{(k+1)} + V_{i,j+1}^{(k)} + V_{i,j-1}^{(k+1)}\right)

SOR (Successive Over-Relaxation)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

이완 계수 :math:`\omega` 를 도입하여 수렴 가속:

.. math::

   V_{i,j}^{new} = (1-\omega)V_{i,j}^{old} + \omega \cdot V_{GS}^{new}

최적 :math:`\omega \approx 2 - \pi\sqrt{2/N}` (격자 크기 :math:`N` 에 따라 결정)

수치 미분 (Gradient)
---------------------

전위로부터 전기장 계산에 사용하는 중앙 차분법:

.. math::

   \frac{\partial V}{\partial x}\bigg|_{i} \approx \frac{V_{i+1} - V_{i-1}}{2\Delta x}

NumPy에서는 ``numpy.gradient(V, dx, dy)`` 로 2D 기울기를 계산합니다.

.. list-table:: 수치 방법 정확도 비교
   :header-rows: 1
   :widths: 30 20 20 30

   * - 방법
     - 오차
     - 적용
     - 코드
   * - Forward difference
     - :math:`O(\Delta x)`
     - 1차 미분
     - ``(f[i+1]-f[i])/dx``
   * - Central difference
     - :math:`O(\Delta x^2)`
     - 1차, 2차 미분
     - ``(f[i+1]-f[i-1])/(2dx)``
   * - RK4
     - :math:`O(\Delta t^4)`
     - ODE 적분
     - 05번 프로그램
   * - FDTD
     - :math:`O(\Delta t^2, \Delta x^2)`
     - 파동 방정식
     - 06, 07번 프로그램
