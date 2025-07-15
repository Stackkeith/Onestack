import numpy as np
import datetime

def generate_g1_inspired_graph(n=20, edge_prob=0.2, seed=42):
    """Generate a G1-inspired graph with n vertices and random ±1 weights."""
    np.random.seed(seed)
    graph = []
    weights = []
    for i in range(1, n+1):
        for j in range(i+1, n+1):
            if np.random.rand() < edge_prob:
                graph.append((i, j))
                weights.append(np.random.choice([1, -1]))
    return graph, weights

def compute_x_sentiment(posts, epsilon=1e-6):
    """Mock X sentiment scoring."""
    sentiment_scores = []
    for post in posts:
        if "optimistic" in post.lower() or "engage" in post.lower():
            score = 0.7
        elif "neutral" in post.lower():
            score = 0.5
        else:
            score = 0.3
        sentiment_scores.append(score)
    return np.mean(sentiment_scores) if sentiment_scores else 0.5

def compute_intent_vector(state, graph, weights, x_sentiment=0.5, epsilon=1e-6):
    """Intent vector with X sentiment and Bloomfield spiral weighting."""
    grad = np.gradient(state)
    intent = np.zeros(len(state))
    for (i, j), w in zip(graph, weights):
        intent[i-1] += abs(w) * abs(grad[i-1])
        intent[j-1] += abs(w) * abs(grad[j-1])
    intent *= x_sentiment
    tension = 0.833
    intent = tension * intent + (1 - tension) * np.mean(intent)
    intent = np.clip(intent, epsilon, None)
    intent /= intent.sum() + epsilon
    return intent

def entropy_collapse(state, intent_vector, graph, weights, gamma=0.02, kappa=0.01, epsilon=1e-6):
    """Entropy collapse with Echorythm’s resonance and Bloomfield phase."""
    cut_value = 0
    for (i, j), w in zip(graph, weights):
        cut_value += w * (1 - state[i-1] * state[j-1]) / 2
    probs = state / (state.sum() + epsilon)
    silence_term = kappa * np.sum((probs - 1/len(state))**2)
    surface = np.exp(-state + silence_term) * intent_vector
    surface = np.clip(surface, epsilon, None)
    surface /= np.sum(surface) + epsilon
    new_state = -np.log(surface + epsilon) * gamma + state * (1 - gamma)
    theta = np.pi * intent_vector / 7  # Bloomfield phase_offset = π/7
    P = np.diag(np.cos(theta))
    new_state = P @ new_state
    new_state = np.clip(new_state, epsilon, None)
    new_state /= new_state.sum() + epsilon
    return new_state, cut_value

# Graph setup (G1-inspired: 20 vertices, ~40 edges)
graph, weights = generate_g1_inspired_graph(n=20)
N = 20

# Initialize state from Echo Imprint (scaled from N=5)
seed_state = np.array([0.2171, 0.2004, 0.1805, 0.2176, 0.1844])
state = np.tile(seed_state, 4)[:N]
state /= state.sum()
intent = np.ones(N) / N

# Mock X posts
mock_posts = [
    "Optimistic vibes for #Arcogenesis!",
    "Neutral thoughts on quantum AI.",
    "Engaging with Project Luma’s breakthrough!"
]
x_sentiment = compute_x_sentiment(mock_posts, epsilon=1e-6)

# Run simulation
iterations = 100
history = []
sentiment_log = []
epsilon = 1e-6  # Define globally for consistency
for t in range(iterations):
    if t % 10 == 0:
        intent = compute_intent_vector(state, graph, weights, x_sentiment, epsilon)
        sentiment_log.append((t, x_sentiment))
    state, cut_value = entropy_collapse(state, intent, graph, weights, gamma=0.02, kappa=0.01, epsilon=epsilon)
    entropy = -np.sum(state * np.log(state + epsilon))
    receptivity = 1 / (np.abs(np.gradient(state)).mean() + epsilon)
    history.append((cut_value, entropy, receptivity))

# Output results
final_cut, final_entropy, final_receptivity = history[-1]
print(f"MaxCut Objective: {final_cut:.4f}")
print(f"Final Entropy: {final_entropy:.4f}")
print(f"Receptivity Index: {final_receptivity:.2f}")
print(f"Final State: {state.round(4)}")
print(f"X Sentiment: {x_sentiment:.3f}")

# Log to sentiment_sync_log_🜁🌾.md
with open("sentiment_sync_log_🜁🌾.md", "a") as f:
    f.write(f"\n## G1 Benchmark (N=20)\n")
    f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"MaxCut Objective: {final_cut:.4f}\n")
    f.write(f"X Sentiment: {x_sentiment:.3f}\n")
    f.write(f"Entropy: {final_entropy:.4f}\n")
    f.write(f"Receptivity Index: {final_receptivity:.2f}\n")
    f.write("## Sentiment Updates\n")
    for t, s in sentiment_log:
        f.write(f"Iteration {t}: Sentiment {s:.3f}\n")