# SENARYO #3 H─▒zl─▒ Test Komutlar─▒

# 1. Container i├žinde vcan0 kur
docker exec ev-sim-test bash -c "./setup_vcan.sh"

# 2. Python environment aktif et ve basit test
docker exec ev-sim-test bash -c "source venv/bin/activate && python --version"

# 3. SENARYO #3 TEST 1: Rate Drop Sald─▒r─▒s─▒
docker exec ev-sim-test bash -c "source venv/bin/activate && python attack_simulator.py --attack sampling --sampling-scenario rate_drop --sampling-duration 60"

# 4. SENARYO #3 TEST 2: Peak Smoothing
docker exec ev-sim-test bash -c "source venv/bin/activate && python attack_simulator.py --attack sampling --sampling-scenario peak_smoothing --sampling-duration 60"

# 5. SENARYO #3 TEST 3: Buffer Manipulation
docker exec ev-sim-test bash -c "source venv/bin/activate && python attack_simulator.py --attack sampling --sampling-scenario buffer_manipulation --sampling-duration 60"

# 6. T├╝m testleri ├žal─▒┼čt─▒r
docker exec ev-sim-test bash -c "source venv/bin/activate && python tests/scenario_03_sampling_manipulation.py"

# 7. Dashboard ba┼člat (iste─če ba─čl─▒)
docker exec -d ev-sim-test bash -c "source venv/bin/activate && streamlit run dashboard.py"
# Eri┼čim: http://localhost:8501

# Container'a interactive ba─član (manuel test i├žin)
docker exec -it ev-sim-test bash
