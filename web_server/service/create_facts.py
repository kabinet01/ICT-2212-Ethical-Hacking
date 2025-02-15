import pickle
import randfacts


def create_pickle_file(filename='facts.pkl', num_facts=5):
    """Create a pickle file with a list of facts."""
    facts = []
    for i in range(num_facts):
        facts.append(randfacts.get_fact())

    with open(filename, 'wb') as f:
        pickle.dump(facts, f)

    print(f"Created {filename} with {num_facts} facts.")
    print("Sample facts:")
    for i in range(len(facts)):
        print(f"  - {facts[i]}")


if __name__ == "__main__":
    create_pickle_file()
