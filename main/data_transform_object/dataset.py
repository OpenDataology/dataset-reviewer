from flask_restplus import fields

from main.util.namespace import user_dataset_review_ns


class DatasetObject:
    # 一般性消息
    dataset_review_msg_resp = user_dataset_review_ns.model("1. dataset_review_msg_resp", {
        'message': fields.String(description='success 或 fail'),
        'notification': fields.String(description='自定义提示内容')
    })

    # 单个数据集审核原始上传信息
    dataset_review_req = user_dataset_review_ns.model("2. dataset_review_req", {
        'name': fields.String(description='数据集名称', required=True),
        'location': fields.String(description='数据集官网链接', required=True),
        'originator': fields.String(description='数据集贡献者', required=True)
    })

    # 单个数据集的AIBOM信息
    pending_aibom = user_dataset_review_ns.model("3. pending_aibom", {
        'id': fields.Integer(description='表pending_aibom中的数据集id，在请求中使用pending_aibom时，必须传入该id', required=True),
        # 数据集AIBOM属性
        'name': fields.String(description='数据集名称', required=True),
        'location': fields.String(description='数据集官网', required=True),
        'originator': fields.String(description='贡献者', required=True),
        'license_location': fields.String(description='许可地址', required=True),
        'concluded_license': fields.String(description='SPDX License List中的许可'),
        'declared_license': fields.String(description='自定义许可'),
        'type': fields.String(description='数据集格式，例如图片、音频、视频等', enum=['image', 'radio', 'video', 'binary', 'others'], required=True),
        'size': fields.String(description='数据集大小', required=True),
        'intended_use': fields.String(description='使用目的', required=True),
        'checksum': fields.String(description='验证'),
        'data_collection_process': fields.String(description='数据收集过程'),
        'known_biases': fields.Boolean(description='是否有已知偏见'),
        'sensitive_personal_information': fields.Boolean(description='是否有个人敏感信息'),
        'offensive_content': fields.Boolean(description='是否有冒犯内容'),
        # 上传用户信息
        'user_id': fields.Integer(description='待补充该AIBOM的用户', required=True),
        # 驳回备注
        'rejection_notes': fields.String(description='仅pending_AIBOM和reject_review路由中使用，若该数据集AIBOM提交后被驳回，可在此备注，其它场景无需使用该属性.'),
    })

    # 数据集的审核结论
    review_result = user_dataset_review_ns.model("4. review_result", {
        'id': fields.Integer(description='表pending_review和review_result中的数据集id，在请求中使用时，必须传入该id', required=True),
        # 数据集AIBOM属性
        'name': fields.String(description='数据集名称', required=True),
        'location': fields.String(description='数据集官网', required=True),
        'originator': fields.String(description='贡献者', required=True),
        'license_location': fields.String(description='许可地址', required=True),
        'concluded_license': fields.String(description='SPDX License List中的许可'),
        'declared_license': fields.String(description='自定义许可'),
        'type': fields.String(description='数据集格式，例如图片、音频、视频等', required=True),
        'size': fields.String(description='数据集大小', required=True),
        'intended_use': fields.String(description='使用目的', required=True),
        'checksum': fields.String(description='验证'),
        'data_collection_process': fields.String(description='数据收集过程'),
        'known_biases': fields.Boolean(description='是否有已知偏见'),
        'sensitive_personal_information': fields.Boolean(description='是否有个人敏感信息'),
        'offensive_content': fields.Boolean(description='是否有冒犯内容'),
        # 上传用户信息
        'user_id': fields.Integer(description='待补充该AIBOM的用户', required=True),
        # 初步review意见
        'review_result_initial': fields.String(description='初步review结论', required=True),
        'is_dataset_commercially_used_initial': fields.Boolean(description='数据集是否可商业使用', required=True),
        'is_dataset_commercially_distributed_initial': fields.Boolean(description='数据集是否可商业分发', required=True),
        'is_product_commercially_published_initial': fields.Boolean(description='数据集是否可集成到产品发布', required=True),
        'right_initial': fields.String(description='初步权利分析'),
        'obligation_initial': fields.String(description='初步责任分析'),
        'limitation_initial': fields.String(description='初步限制分析'),
        'notes_initial': fields.String(description='初步review的备注'),
        # 最终review意见
        'review_result_final': fields.String(description='最终review结论', required=True),
        'is_dataset_commercially_used_final': fields.Boolean(description='数据集是否可商业使用', required=True),
        'is_dataset_commercially_distributed_final': fields.Boolean(description='数据集是否可商业分发', required=True),
        'is_product_commercially_published_final': fields.Boolean(description='数据集是否可集成到产品发布', required=True),
        'right_final': fields.String(description='最终权利分析'),
        'obligation_final': fields.String(description='最终责任分析'),
        'limitation_final': fields.String(description='最终限制分析'),
        'notes_final': fields.String(description='最终review的备注'),
    })

    # 批量数据集审核上传原始信息
    dataset_review_list_req = user_dataset_review_ns.model("5. dataset_review_list_req", {
        'user_id': fields.Integer(description='用户id', required=True),
        'dataset_review_list': fields.List(fields.Nested(dataset_review_req), description='单个数据集审核原始上传信息', required=True)
    })

    # 批量数据集是否已审核检测分类
    dataset_is_reviewed_list_resp = user_dataset_review_ns.model("6. dataset_is_reviewed_list_resp", {
        'review_result_list': fields.List(fields.Nested(review_result), description='批量数据集的审核结论'),
        'pending_aibom_list': fields.List(fields.Nested(pending_aibom), description='批量数据集的AIBOM信息'),
        'message': fields.String(description='success 或 fail'),
        'notification': fields.String(description='自定义提示内容')
    })

    # 批量保存数据集的AIBOM信息
    pending_aibom_list_req = user_dataset_review_ns.model("7. pending_aibom_list_req", {
        'pending_aibom_list': fields.List(fields.Nested(pending_aibom), description='批量数据集的AIBOM信息', required=True)
    })

    # 批量返回数据集的AIBOM信息
    pending_aibom_list_resp = user_dataset_review_ns.model("8. pending_aibom_list_resp", {
        'pending_aibom_list': fields.List(fields.Nested(pending_aibom), description='批量数据集的AIBOM信息'),
        'message': fields.String(description='success 或 fail'),
        'notification': fields.String(description='自定义提示内容')
    })

    # 状态回退，若位于pending AIBOM状态，则删除，若位于pending review状态，则回退至pending AIBOM
    dataset_state_rollback_req = user_dataset_review_ns.model("9. dataset_state_rollback_req", {
        'user_id': fields.Integer(description='用户id', required=True),
        'pending_aibom_review_ids': fields.List(fields.Integer, description='pending_aibom或pending_review表中的数据集id', required=True),
        'rejection_notes': fields.List(fields.String, description='拒绝review的notes，rejection_notes的数量<=pending_aibom_review_ids的数量')
    })

    # 批量保存数据集review信息
    pending_review_list_req = user_dataset_review_ns.model("10. pending_review_list_req", {
        'pending_review_list': fields.List(fields.Nested(review_result), description='批量数据集的审核结论', required=True)
    })

    # 批量返回数据集的待审核信息
    pending_review_list_resp = user_dataset_review_ns.model("11. pending_review_list_resp", {
        'pending_review_list': fields.List(fields.Nested(review_result), description='批量数据集的审核结论'),
        'message': fields.String(description='success 或 fail'),
        'notification': fields.String(description='自定义提示内容')
    })

    # 批量返回数据集的审核结论信息
    review_result_list_resp = user_dataset_review_ns.model("12. review_result_list_resp", {
        'review_result_list': fields.List(fields.Nested(review_result), description='批量数据集的审核结论'),
        'message': fields.String(description='success 或 fail'),
        'notification': fields.String(description='自定义提示内容')
    })

    # 单个License上传信息
    dataset_license = user_dataset_review_ns.model("13. dataset_license", {
        'full_name': fields.String(description='License全称', required=True),
        'identifier': fields.String(description='License标识符', required=True),
        'fsf_free_libre': fields.String(description='fsf_free/libre', required=False),
        'osi_approved': fields.String(description='osi approved', required=False)
    })

    # 批量License上传信息
    dataset_license_list_req = user_dataset_review_ns.model("14. dataset_review_list_req", {
        'user_id': fields.Integer(description='用户id', required=True),
        'dataset_license_list': fields.List(fields.Nested(dataset_license), description='批量License上传信息', required=True)
    })

    # 批量License上传信息结果
    dataset_license_list_resp = user_dataset_review_ns.model("15. dataset_license_list_resp", {
        'license_success_list': fields.List(fields.Nested(dataset_license), description='上传成功的License'),
        'license_fail_list': fields.List(fields.Nested(dataset_license), description='上传失败的License'),
        'message': fields.String(description='success 或 fail'),
        'notification': fields.String(description='自定义提示内容')
    })

    # 批量License上传信息结果
    license_list_resp = user_dataset_review_ns.model("16. license_list_resp", {
        'spdx_license_list': fields.List(fields.Nested(dataset_license), description='License list'),
        'message': fields.String(description='success 或 fail'),
        'notification': fields.String(description='自定义提示内容')
    })

    string_req = user_dataset_review_ns.model("17. String Req", {
        'text': fields.String(description='text'),
    })
