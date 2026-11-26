from collections import deque

def parse_set(prompt):
    """Membaca himpunan yang dipisahkan koma."""
    return [x.strip() for x in input(prompt).split(",") if x.strip()]

def read_nfa():
    print("\n=== INPUT NFA ===")
    states = parse_set("Masukkan state (contoh: q0,q1,q2): ")
    alphabet = parse_set("Masukkan alfabet (contoh: 0,1): ")
    start = input("Masukkan state awal: ").strip()
    finals = parse_set("Masukkan state akhir/final (pisahkan koma): ")

    if not states or not alphabet:
        raise ValueError("State dan alfabet tidak boleh kosong.")
    if start not in states:
        raise ValueError("State awal harus terdaftar dalam himpunan state.")
    if any(f not in states for f in finals):
        raise ValueError("Semua state final harus terdaftar.")

    transitions = {}
    print("\nMasukkan tujuan transisi untuk setiap pasangan state dan simbol.")
    print("Jika tidak ada transisi, tekan Enter. Pisahkan beberapa tujuan dengan koma.")
    for state in states:
        for symbol in alphabet:
            raw = input(f"δ({state}, {symbol}) = ").strip()
            destinations = [x.strip() for x in raw.split(",") if x.strip()]
            if any(d not in states for d in destinations):
                raise ValueError("Tujuan transisi harus merupakan state yang terdaftar.")
            transitions[(state, symbol)] = set(destinations)

    return {
        "states": states,
        "alphabet": alphabet,
        "start": start,
        "finals": set(finals),
        "transitions": transitions
    }

def show_nfa(nfa):
    print("\n--- TABEL TRANSISI NFA ---")
    print("State\t" + "\t".join(nfa["alphabet"]))
    for state in nfa["states"]:
        cells = []
        for symbol in nfa["alphabet"]:
            dest = sorted(nfa["transitions"][(state, symbol)])
            cells.append("{" + ",".join(dest) + "}")
        print(state + "\t" + "\t".join(cells))
    print("State awal :", nfa["start"])
    print("State final:", "{" + ",".join(sorted(nfa["finals"])) + "}")

def run_nfa(nfa, word, verbose=True):
    current = {nfa["start"]}
    if verbose:
        print("\nSimulasi NFA:")
        print("Input:", word if word else "(ε/kosong)")
        print("State awal:", current)
    for symbol in word:
        if symbol not in nfa["alphabet"]:
            print(f"Simbol '{symbol}' tidak termasuk alfabet.")
            return False
        next_states = set()
        for state in current:
            next_states |= nfa["transitions"][(state, symbol)]
        current = next_states
        if verbose:
            print(f"Setelah membaca '{symbol}': {current}")
    accepted = bool(current & nfa["finals"])
    if verbose:
        print("State akhir yang dicapai:", current)
        print("Hasil:", "DITERIMA" if accepted else "DITOLAK")
    return accepted

def convert_nfa_to_dfa(nfa):
    """Konstruksi himpunan bagian (subset construction)."""
    start_set = frozenset([nfa["start"]])
    queue = deque([start_set])
    discovered = {start_set}
    transitions = {}
    while queue:
        subset = queue.popleft()
        for symbol in nfa["alphabet"]:
            destination = set()
            for state in subset:
                destination |= nfa["transitions"][(state, symbol)]
            target = frozenset(destination)
            transitions[(subset, symbol)] = target
            if target not in discovered:
                discovered.add(target)
                queue.append(target)

    # Nama state DFA dibuat S0, S1, ... sesuai urutan ditemukan.
    ordered = list(discovered)
    ordered.sort(key=lambda s: (len(s), sorted(s)))
    # Pastikan state awal selalu S0.
    ordered.remove(start_set)
    ordered.insert(0, start_set)
    names = {subset: f"S{i}" for i, subset in enumerate(ordered)}
    dfa_transitions = {
        (names[src], sym): names[dst]
        for (src, sym), dst in transitions.items()
    }
    dfa_finals = {
        names[subset] for subset in ordered
        if set(subset) & nfa["finals"]
    }
    return {
        "states": [names[s] for s in ordered],
        "subsets": {names[s]: set(s) for s in ordered},
        "alphabet": nfa["alphabet"],
        "start": "S0",
        "finals": dfa_finals,
        "transitions": dfa_transitions
    }

def show_dfa(dfa):
    print("\n--- HASIL KONVERSI DFA ---")
    print("State DFA\tHimpunan state NFA\t" + "\t".join(dfa["alphabet"]))
    for state in dfa["states"]:
        cells = [dfa["transitions"][(state, sym)] for sym in dfa["alphabet"]]
        print(f"{state}\t\t{sorted(dfa['subsets'][state])}\t\t" + "\t".join(cells))
    print("State awal :", dfa["start"])
    print("State final:", "{" + ",".join(sorted(dfa["finals"])) + "}")

def run_dfa(dfa, word):
    current = dfa["start"]
    print("\nSimulasi DFA:")
    print("Input:", word if word else "(ε/kosong)")
    print("State awal:", current)
    for symbol in word:
        if symbol not in dfa["alphabet"]:
            print(f"Simbol '{symbol}' tidak termasuk alfabet.")
            return False
        current = dfa["transitions"][(current, symbol)]
        print(f"Setelah membaca '{symbol}': {current}")
    accepted = current in dfa["finals"]
    print("State akhir:", current)
    print("Hasil:", "DITERIMA" if accepted else "DITOLAK")
    return accepted

def main():
    print("=" * 55)
    print("     PROGRAM NFA, DFA, DAN KONVERSI NFA KE DFA")
    print("=" * 55)
    try:
        nfa = read_nfa()
        show_nfa(nfa)
        dfa = convert_nfa_to_dfa(nfa)
        show_dfa(dfa)

        while True:
            print("\nMENU")
            print("1. Uji string pada NFA")
            print("2. Uji string pada DFA hasil konversi")
            print("3. Uji string pada keduanya")
            print("0. Keluar")
            choice = input("Pilih menu: ").strip()
            if choice == "0":
                print("Program selesai.")
                break
            if choice not in {"1", "2", "3"}:
                print("Pilihan tidak valid.")
                continue
            word = input("Masukkan string yang akan diuji (boleh kosong): ").strip()
            if choice in {"1", "3"}:
                nfa_result = run_nfa(nfa, word)
            if choice in {"2", "3"}:
                dfa_result = run_dfa(dfa, word)
            if choice == "3":
                print("\nPemeriksaan kesetaraan hasil:")
                print("NFA dan DFA memberikan hasil yang sama." if nfa_result == dfa_result
                      else "PERINGATAN: hasil berbeda, periksa input atau program.")
    except ValueError as error:
        print("Kesalahan input:", error)

if __name__ == "__main__":
    main()
