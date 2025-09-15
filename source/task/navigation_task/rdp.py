from math import sqrt
from source.view_and_move.cvars import POINT_TYPE_TARGET


def distance(a, b):
    return  sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def point_line_distance(point, start, end):
    if (start == end):
        return distance(point, start)
    else:
        n = abs(
            (end[0] - start[0]) * (start[1] - point[1]) -
            (start[0] - point[0]) * (end[1] - start[1])
        )
        d = sqrt(
            (end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2
        )
        return n / d


# def rdp(point_list, target_index_list, epsilon, abs_target_index_list):
#     if abs_target_index_list is None:
#         abs_target_index_list = []

#     dmax = 0.0
#     index = 0
#     for i in range(1, len(target_index_list) - 1):
#         point = point_list[target_index_list[i]].position
#         start = point_list[target_index_list[0]].position
#         end = point_list[target_index_list[-1]].position
#         d = point_line_distance(point, start, end)
#         if d > dmax:
#             index = i
#             dmax = d
    
#     # RDP 优化
#     if dmax >= epsilon and 0 < index < len(target_index_list)-1:
#         results = rdp(point_list, target_index_list[:index+1], epsilon, target_index_list)[:-1] + \
#                   rdp(point_list, target_index_list[index:], epsilon, target_index_list)
#     else:
#         results = [target_index_list[0], target_index_list[-1]]
    
#     # 确保abs被保留
#     final_results = []
#     for p in target_index_list:
#         if p in results or p in abs_target_index_list:
#             if not final_results or final_results[-1] != p:
#                 final_results.append(p)

#     return final_results

def rdp_optimize(pp_list, start_target_point_index, end_target_point_index, epsilon):
    '''利用二分法，不断找到转折过大的点，设为target'''
    if start_target_point_index + 1 == end_target_point_index:
        return
    dmax = 0.0
    index = 0
    start_position = pp_list[start_target_point_index].position
    end_position = pp_list[end_target_point_index].position
    for i in range(start_target_point_index+1, end_target_point_index):
        p = pp_list[i].position
        d = point_line_distance(p, start_position, end_position)
        if d > dmax:
            index = i
            dmax = d
    
    if dmax > epsilon:
        pp_list[index].point_type = POINT_TYPE_TARGET
        rdp_optimize(pp_list, start_target_point_index, index, epsilon)
        rdp_optimize(pp_list, index, end_target_point_index, epsilon)

