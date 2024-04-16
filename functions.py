from imports import *
from load_data import load_data
from network_operations import create_network, get_travel_time
from simulated_annealing import simulated_annealing
from theta_operations import update_theta

def run_simulation(file_path, iterations, alpha):
    data = load_data(file_path)
    G = create_network(data)
    start, end = 286, 1007  # Assume start and end points are given
    shortest_path, shortest_time = simulated_annealing(G, start, end, 100, 0.95, 1000)
    print(f"Shortest path: {shortest_path}, Shortest time: {shortest_time:.2f}")
    time_limit = 1.1 * shortest_time  # Set time limit as 110% of shortest time

    shortest_path, shortest_time = simulated_annealing(G, start, end, 100, 0.95, 1000)
    print(f"Shortest path: {shortest_path}, Shortest time: {shortest_time:.2f}")
    time_limit = 1.1 * shortest_time  # 设置时间限制为最短时间
    # 初始化 theta 值
    for u, v in G.edges():
        G[u][v]['theta'] = 0
    # 确保转换为整型，如果节点标识符在图中是整型的话
    shortest_path = [int(node) for node in shortest_path]

    # 遍历最短路径中的每对相邻节点
    for i in range(len(shortest_path) - 1):
        u = shortest_path[i]
        v = shortest_path[i + 1]

        # 检查这条边是否存在于图中
        if G.has_edge(u, v):
            # 如果存在，更新这条边的 theta 值为 1
            G[u][v]['theta'] = 3

    # 运行模拟
    success_rates = []
    success_count = 0
    # 生成一个新的 OD 对
    # start, end = np.random.choice(G.nodes(), 2, replace=False)
    # while start == end:
    #     start, end = np.random.choice(G.nodes(), 2, replace=False)
    for episode in range(iterations):
        alpha = 0.9999 * alpha  # 逐渐降低学习率
        path = [start]  # 初始化路径为起点
        current_node = start
        reward = -0.3
        # 初始化记录边和概率的列表
        selected_edges_probs = []

        while current_node != end:
            # 确定基于条件的可用边
            available_edges = []
            for u, v, data in G.out_edges(current_node, data=True):
                if data['edge_type'] == 'edge1' or (data['edge_type'] == 'edge2' and random.random() < data['p']):
                    available_edges.append((v, data['theta']))
                    # print(available_edges)

            # 如果没有可用的边，处理这个场景
            if not available_edges:
                break
            # 计算转移概率
            thetas = np.array([theta for _, theta in available_edges])
            probabilities = np.exp(thetas) / np.sum(np.exp(thetas))
            # print(f"Node: {current_node}, Available edges: {available_edges}, Probabilities: {probabilities}")

            # 选取下一节点和记录选择的边及其概率
            chosen_index = np.random.choice(range(len(available_edges)), p=probabilities)
            next_node, _ = available_edges[chosen_index]

            # 记录选中的边和概率
            selected_edges_probs.append((current_node, next_node, probabilities[chosen_index]))
            path.append(next_node)
            current_node = next_node

        # 计算奖励
        travel_time = sum(get_travel_time(G[u][v]['weight'], G[u][v]['sigma']) for u, v in zip(path[:-1], path[1:]))
        if travel_time <= time_limit:
            success_count += 1
            reward = 10
            # print(f"Travel time: {travel_time}")

        update_theta(G, selected_edges_probs, reward, alpha)

        # 记录成功率

        success_rate = success_count / (episode + 1)
        print(f"Episode: {episode + 1}, Success rate: {success_rate:.2f}")
        success_rates.append(success_rate)

    # 绘制成功率曲线
    plt.plot(success_rates)
    plt.xlabel('Episode')
    plt.ylabel('On-Time Arrival Rate')
    plt.title('On-Time Arrival Rate Over Episodes')
    plt.show()