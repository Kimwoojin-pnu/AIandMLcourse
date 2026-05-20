개요
====

Week 10은 **전자기학(Electromagnetism)** 을 수치적으로 시뮬레이션하는 10개의 실습 프로그램으로 구성됩니다.
Python과 NumPy/Matplotlib를 사용하여 전기장, 자기장, 전자기파 전파를 계산하고 시각화합니다.

학습 목표
---------

1. 전기장 및 전위의 개념과 시각화
2. 맥스웰 방정식의 FDTD 수치 해법
3. 라플라스 방정식의 반복법 풀이
4. 전자기파의 구조와 전파 이해

맥스웰 방정식
-------------

전자기학의 기초가 되는 맥스웰 방정식:

.. math::

   \nabla \cdot \mathbf{E} = \frac{\rho}{\varepsilon_0}

.. math::

   \nabla \cdot \mathbf{B} = 0

.. math::

   \nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}

.. math::

   \nabla \times \mathbf{B} = \mu_0 \mathbf{J} + \mu_0\varepsilon_0 \frac{\partial \mathbf{E}}{\partial t}

물리 상수
---------

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - 상수
     - 값
     - 설명
   * - :math:`k_e`
     - :math:`8.99 \times 10^9\ \mathrm{N \cdot m^2/C^2}`
     - 쿨롱 상수
   * - :math:`\mu_0`
     - :math:`4\pi \times 10^{-7}\ \mathrm{T \cdot m/A}`
     - 진공 투자율
   * - :math:`\varepsilon_0`
     - :math:`8.85 \times 10^{-12}\ \mathrm{F/m}`
     - 진공 유전율
   * - :math:`c`
     - :math:`3 \times 10^8\ \mathrm{m/s}`
     - 진공 내 광속

프로그램 구성
-------------

.. list-table::
   :header-rows: 1
   :widths: 10 40 50

   * - 번호
     - 파일
     - 내용
   * - 01
     - ``01_electric_field_basics.py``
     - 단일 점전하 전기장 시각화
   * - 02
     - ``02_electric_potential.py``
     - 전위 및 등전위선
   * - 03
     - ``03_electric_field_lines.py``
     - 전기력선 시각화
   * - 04
     - ``04_magnetic_field_basics.py``
     - 직선 전류의 자기장
   * - 05
     - ``05_lorentz_force.py``
     - 하전 입자의 운동 (로렌츠 힘)
   * - 06
     - ``06_maxwell_1d.py``
     - 1D 전자기파 FDTD
   * - 07
     - ``07_maxwell_2d.py``
     - 2D 전자기파 FDTD
   * - 08
     - ``08_multiple_charges.py``
     - 다중 점전하 시스템
   * - 09
     - ``09_em_wave_animation.py``
     - 전자기파 3D 애니메이션
   * - 10
     - ``10_conductor_potential.py``
     - 라플라스 방정식 (도체 전위)

실행 방법
---------

개별 실행::

   cd week10
   python 01_electric_field_basics.py

전체 일괄 실행::

   for f in 0*.py 1*.py; do python $f; done

출력 파일은 ``week10/outputs/`` 디렉토리에 저장됩니다.

.. note::

   한글 폰트 지원을 위해 Windows에서는 **Malgun Gothic**, macOS에서는 **AppleGothic** 폰트를 자동으로 감지합니다.
