from flask import request
from flask import json

from flask import send_from_directory, make_response

from flask_restplus import Resource
from flask_restplus import marshal

from main.data_transform_object.dataset import DatasetObject
from main.data_transform_object.user import UserObject
from main.data_transform_object.admin import AdminObject

from main.util.namespace import user_dataset_review_ns, auth_dataset_review_ns
from main.service import dataset_review


@user_dataset_review_ns.route("/review_upload")
class ReviewUpload(Resource):
    @user_dataset_review_ns.expect(DatasetObject.dataset_review_list_req)
    @user_dataset_review_ns.response(200, 'success', model=DatasetObject.dataset_is_reviewed_list_resp)
    @user_dataset_review_ns.response(403, 'fail', model=DatasetObject.dataset_review_msg_resp)
    def post(self):
        """数据集review上传，直接返回已review部分的数据集结论，未审核过的部分会放入pending_AIBOM中，待调用方补充AIBOM信息"""
        dataset_review_list_req = json.loads(
            request.data)  # Parse request into a dictionary

        # Execute the specific method, and get the returned dictionary
        user_id = dataset_review_list_req['user_id']
        dataset_review_list = dataset_review_list_req['dataset_review_list']
        response_dict = dataset_review.review_upload(
            user_id, dataset_review_list)

        # success or fail
        status_code = 200 if response_dict['message'] == 'success' else 403

        model_ret = DatasetObject.dataset_is_reviewed_list_resp if status_code == 200 else DatasetObject.dataset_review_msg_resp

        return marshal(response_dict, model_ret), status_code


@user_dataset_review_ns.route("/review_upload_by_file")
class ReviewUploadByFile(Resource):
    @user_dataset_review_ns.expect(DatasetObject.dataset_review_list_req)
    @user_dataset_review_ns.response(200, 'success', model=DatasetObject.dataset_is_reviewed_list_resp)
    @user_dataset_review_ns.response(403, 'fail', model=DatasetObject.dataset_review_msg_resp)
    def post(self):
        """数据集review通过文件批量上传，直接返回已review部分的数据集结论，未审核过的部分会放入pending_AIBOM中，待调用方补充AIBOM信息"""
        user_id = request.form.get("user_id")
        dataset_review_list_req = request.files.get('dataset_review_list')

        dataset_review_list = dataset_review.file_convert_dataset(
            user_id, dataset_review_list_req)

        if dataset_review_list['message'] == 'success':
            dataset_review_list = dataset_review_list['notification']
            # Execute the specific method, and get the returned dictionary
            response_dict = dataset_review.review_upload(
                user_id, dataset_review_list)
        else:
            response_dict = dataset_review_list

        # success or fail
        status_code = 200 if response_dict['message'] == 'success' else 403

        model_ret = DatasetObject.dataset_is_reviewed_list_resp if status_code == 200 else DatasetObject.dataset_review_msg_resp

        return marshal(response_dict, model_ret), status_code


@user_dataset_review_ns.route("/pending_AIBOM")
class PendingAIBOM(Resource):
    @user_dataset_review_ns.expect(UserObject.AIBOM_user)
    @user_dataset_review_ns.response(200, 'success', model=DatasetObject.pending_aibom_list_resp)
    @user_dataset_review_ns.response(403, 'fail', model=DatasetObject.dataset_review_msg_resp)
    def get(self):
        """通过该user_id获取需要补充AIBOM信息的数据集列表"""
        user_id = int(request.args.get('user_id', ''))

        # Execute the specific method, and get the returned dictionary
        response_dict = dataset_review.get_pending_aibom_by_user(user_id)

        # success or fail
        status_code = 200 if response_dict['message'] == 'success' else 403

        model_ret = DatasetObject.pending_aibom_list_resp if status_code == 200 else DatasetObject.dataset_review_msg_resp

        return marshal(response_dict, model_ret), status_code


@user_dataset_review_ns.route("/save_AIBOM")
class SaveAIBOM(Resource):
    @user_dataset_review_ns.expect(DatasetObject.pending_aibom_list_req)
    @user_dataset_review_ns.response(200, 'success', model=DatasetObject.dataset_review_msg_resp)
    @user_dataset_review_ns.response(403, 'fail', model=DatasetObject.dataset_review_msg_resp)
    def post(self):
        """临时保存该userid所补充AIBOM信息"""
        hashmap = json.loads(request.data)
        pending_aibom_list = hashmap.get('pending_aibom_list', '')

        # Execute the specific method, and get the returned dictionary
        response_dict = dataset_review.save_pending_aibom_list(
            pending_aibom_list)

        # success or fail
        status_code = 200 if response_dict['message'] == 'success' else 403

        model_ret = DatasetObject.dataset_review_msg_resp

        return marshal(response_dict, model_ret), status_code


@user_dataset_review_ns.route("/submit_AIBOM")
class SubmitAIBOM(Resource):
    @user_dataset_review_ns.expect(DatasetObject.pending_aibom_list_req)
    @user_dataset_review_ns.response(200, 'success', model=DatasetObject.dataset_review_msg_resp)
    @user_dataset_review_ns.response(403, 'fail', model=DatasetObject.pending_aibom_list_resp)
    def post(self):
        """提交该userid所补充AIBOM信息，
        若必填信息格式不正确或空缺会返回对应的数据集列表，正确的部分数据集发送至review侧，并移除pending AIBOM状态.
        格式检查：name、location、originator、license_location、type、size、intended_use、user_id不为空，concluded_license和declared_license不能同时为空。
        """
        hashmap = json.loads(request.data)
        pending_aibom_list = hashmap.get('pending_aibom_list', '')

        # Execute the specific method, and get the returned dictionary
        dataset_review.save_pending_aibom_list(pending_aibom_list)  # 在提交前先临时保存
        response_dict = dataset_review.submit_pending_aibom_list(
            pending_aibom_list)

        # success or fail
        status_code = 200 if response_dict['message'] == 'success' else 403

        model_ret = DatasetObject.dataset_review_msg_resp if status_code == 200 else DatasetObject.pending_aibom_list_resp

        return marshal(response_dict, model_ret), status_code


@user_dataset_review_ns.route("/remove_AIBOM")
class RemoveAIBOM(Resource):
    @user_dataset_review_ns.expect(DatasetObject.dataset_state_rollback_req)
    @user_dataset_review_ns.response(200, 'success', model=DatasetObject.dataset_review_msg_resp)
    @user_dataset_review_ns.response(403, 'fail', model=DatasetObject.dataset_review_msg_resp)
    def post(self):
        """支持用户在补充填写AIBOM信息时可选择删除某些数据集"""
        hashmap = json.loads(request.data)
        user_id = hashmap.get('user_id', "")
        pending_aibom_ids = set(hashmap.get('pending_aibom_review_ids', ''))

        # Execute the specific method, and get the returned dictionary
        response_dict = dataset_review.remove_pending_aibom_list(
            user_id, pending_aibom_ids)

        # success or fail
        status_code = 200 if response_dict['message'] == 'success' else 403

        model_ret = DatasetObject.dataset_review_msg_resp

        return marshal(response_dict, model_ret), status_code


@user_dataset_review_ns.route("/get_license")
class GetLicense(Resource):
    @user_dataset_review_ns.expect(DatasetObject.string_req)
    @user_dataset_review_ns.response(200, 'success', model=DatasetObject.license_list_resp)
    @user_dataset_review_ns.response(403, 'fail', model=DatasetObject.dataset_review_msg_resp)
    def get(self):
        """通过text获取满足模糊查询的license列表，若不传入text则默认获取所有license列表"""
        text = request.args.get('text', '')

        # Execute the specific method, and get the returned dictionary
        response_dict = dataset_review.get_dataset_license_list(text)

        # success or fail
        status_code = 200 if response_dict['message'] == 'success' else 403

        model_ret = DatasetObject.license_list_resp if status_code == 200 else DatasetObject.dataset_review_msg_resp

        return marshal(response_dict, model_ret), status_code


@auth_dataset_review_ns.route("/is_admin")
class IsAdmin(Resource):
    @auth_dataset_review_ns.expect(AdminObject.Admin_user_req)
    @auth_dataset_review_ns.response(200, 'success', model=DatasetObject.dataset_review_msg_resp)
    @auth_dataset_review_ns.response(403, 'fail', model=DatasetObject.dataset_review_msg_resp)
    def post(self):
        """获取用户是否为admin，成功返回success，失败返回fail"""
        hashmap = json.loads(request.data)

        user_id = hashmap.get('user_id', '')
        account = hashmap.get('account', '')

        # Execute the specific method, and get the returned dictionary
        response_dict = dataset_review.is_admin(user_id, account)

        # success or fail
        status_code = 200 if response_dict['message'] == 'success' else 403

        model_ret = DatasetObject.dataset_review_msg_resp

        return marshal(response_dict, model_ret), status_code


@auth_dataset_review_ns.route("/pending_review")
class PendingReview(Resource):
    @auth_dataset_review_ns.expect(UserObject.AIBOM_user)
    @auth_dataset_review_ns.response(200, 'success', model=DatasetObject.pending_review_list_resp)
    @auth_dataset_review_ns.response(403, 'fail', model=DatasetObject.dataset_review_msg_resp)
    def get(self):
        """通过user_id获取所该用户待审批的数据集，若不填入user_id则获取所有待审批数据集"""
        user_id = int(request.args.get('user_id', -1))

        # Execute the specific method, and get the returned dictionary
        response_dict = dataset_review.get_pending_review_list(user_id)

        # success or fail
        status_code = 200 if response_dict['message'] == 'success' else 403

        model_ret = DatasetObject.pending_review_list_resp if status_code == 200 else DatasetObject.dataset_review_msg_resp

        return marshal(response_dict, model_ret), status_code


@auth_dataset_review_ns.route("/save_review")
class SaveReview(Resource):
    @auth_dataset_review_ns.expect(DatasetObject.pending_review_list_req)
    @auth_dataset_review_ns.response(200, 'success', model=DatasetObject.dataset_review_msg_resp)
    @auth_dataset_review_ns.response(403, 'fail', model=DatasetObject.dataset_review_msg_resp)
    def post(self):
        """临时保存该审核者填写的信息"""
        hashmap = json.loads(request.data)
        pending_review_list = hashmap.get('pending_review_list', '')

        # Execute the specific method, and get the returned dictionary
        response_dict = dataset_review.save_pending_review_list(
            pending_review_list)

        # success or fail
        status_code = 200 if response_dict['message'] == 'success' else 403

        model_ret = DatasetObject.dataset_review_msg_resp

        return marshal(response_dict, model_ret), status_code


@auth_dataset_review_ns.route("/reject_review")
class RejectReview(Resource):
    @auth_dataset_review_ns.expect(DatasetObject.dataset_state_rollback_req)
    @auth_dataset_review_ns.response(200, 'success', model=DatasetObject.pending_aibom_list_resp)
    @auth_dataset_review_ns.response(403, 'fail', model=DatasetObject.dataset_review_msg_resp)
    def post(self):
        """审核者判断该AIBOM补充信息不完善，拒绝review，此时状态从pending review回退到pending AIBOM，并且审核者可提示用户该数据集的AIBOM问题所在"""
        hashmap = json.loads(request.data)
        user_id = hashmap.get('user_id', "")
        pending_review_ids = hashmap.get('pending_aibom_review_ids', '')
        rejection_notes = hashmap.get('rejection_notes', "")

        # Execute the specific method, and get the returned dictionary
        response_dict = dataset_review.reject_review(
            user_id, pending_review_ids, rejection_notes)

        # success or fail
        status_code = 200 if response_dict['message'] == 'success' else 403

        model_ret = DatasetObject.pending_aibom_list_resp if status_code == 200 else DatasetObject.dataset_review_msg_resp

        return marshal(response_dict, model_ret), status_code


@auth_dataset_review_ns.route("/submit_review")
class SubmitReview(Resource):
    @auth_dataset_review_ns.expect(DatasetObject.pending_review_list_req)
    @auth_dataset_review_ns.response(200, 'success', model=DatasetObject.dataset_review_msg_resp)
    @auth_dataset_review_ns.response(403, 'fail', model=DatasetObject.pending_review_list_resp)
    def post(self):
        """提交该审核者的review信息从pending_review到review_result"""
        hashmap = json.loads(request.data)
        pending_review_list = hashmap.get('pending_review_list', '')

        # Execute the specific method, and get the returned dictionary
        dataset_review.save_pending_review_list(
            pending_review_list)  # 在提交前先临时保存
        response_dict = dataset_review.submit_pending_review_list(
            pending_review_list)

        # success or fail
        status_code = 200 if response_dict['message'] == 'success' else 403

        model_ret = DatasetObject.dataset_review_msg_resp if status_code == 200 else DatasetObject.pending_review_list_resp

        return marshal(response_dict, model_ret), status_code


@auth_dataset_review_ns.route("/review_result")
class ReviewResult(Resource):
    @auth_dataset_review_ns.expect(UserObject.AIBOM_user)
    @auth_dataset_review_ns.response(200, 'success', model=DatasetObject.review_result_list_resp)
    @auth_dataset_review_ns.response(403, 'fail', model=DatasetObject.dataset_review_msg_resp)
    def get(self):
        """通过user_id获取该用户所有已审核完成的数据集，若不填入user_id则获取所有已审批完成数据集"""
        user_id = int(request.args.get('user_id', -1))

        # Execute the specific method, and get the returned dictionary
        response_dict = dataset_review.get_review_result_list(user_id)

        # success or fail
        status_code = 200 if response_dict['message'] == 'success' else 403

        model_ret = DatasetObject.review_result_list_resp if status_code == 200 else DatasetObject.dataset_review_msg_resp

        return marshal(response_dict, model_ret), status_code


@auth_dataset_review_ns.route("/review_result_download")
class ReviewResultDownload(Resource):
    @auth_dataset_review_ns.expect(UserObject.AIBOM_user)
    @auth_dataset_review_ns.response(403, 'fail', model=DatasetObject.dataset_review_msg_resp)
    def post(self):
        """通过user_id以csv形式下载所该用户所有已审核完成的数据集，若不填入user_id则默认下载所有已审批完成数据集"""
        user_id = json.loads(request.data).get('user_id', -1)
        user_id = -1 if user_id == "" or user_id is None else user_id

        # Execute the specific method, and get the returned dictionary
        response_dict = dataset_review.get_review_result_list(user_id)

        if response_dict['message'] == 'success':
            response_dict = dataset_review.review_result_download(
                user_id, response_dict['review_result_list'])

        # success or fail
        status_code = 200 if response_dict['message'] == 'success' else 403

        model_ret = DatasetObject.review_result_list_resp if status_code == 200 else DatasetObject.dataset_review_msg_resp

        if status_code == 404:
            return marshal(response_dict, model_ret), status_code
        else:
            res = make_response(send_from_directory(
                response_dict['download_path'], response_dict['file_name'], as_attachment=True))
            res.headers["Cache-Control"] = "no_store"
            res.headers["max-age"] = 1
            return res


@auth_dataset_review_ns.route("/license_upload_by_file")
class LicenseUploadByFile(Resource):
    @auth_dataset_review_ns.expect(DatasetObject.dataset_license_list_req)
    @auth_dataset_review_ns.response(200, 'success', model=DatasetObject.dataset_review_msg_resp)
    @auth_dataset_review_ns.response(403, 'fail', model=DatasetObject.dataset_license_list_resp)
    def post(self):
        """License通过文件批量上传，已存在的不会重复添加，会放入fail列表中，成功的会放入success列表中，若都成功，则只返回成功提示"""
        user_id = request.form.get("user_id")
        dataset_license_list_req = request.files.get('dataset_license_list')

        dataset_license_list_req = dataset_review.file_convert_license(
            user_id, dataset_license_list_req)

        if dataset_license_list_req['message'] == 'success':
            dataset_license_list = dataset_license_list_req['notification']
            # Execute the specific method, and get the returned dictionary
            response_dict = dataset_review.license_upload(
                user_id, dataset_license_list)
        else:
            response_dict = dataset_license_list_req

        # success or fail
        status_code = 200 if response_dict['message'] == 'success' else 403

        model_ret = DatasetObject.dataset_review_msg_resp if status_code == 200 else DatasetObject.dataset_license_list_resp

        return marshal(response_dict, model_ret), status_code
