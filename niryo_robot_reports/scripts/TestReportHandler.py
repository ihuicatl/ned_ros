import json
import rospy
from datetime import datetime

from niryo_robot_reports.TestReport import TestReport

# msg
from std_msgs.msg import String
from niryo_robot_msgs.msg import CommandStatus


class TestReportHandler:
    def __init__(self, cloud_api, reports_path, add_report_db, rm_report_db, get_all_files_paths_db):
        self.__cloud_api = cloud_api
        self.__reports_path = reports_path
        self.__add_report_db = add_report_db
        self.__rm_report_db = rm_report_db
        self.__get_all_files_paths_db = get_all_files_paths_db

        self.__send_failed_test_reports()

        rospy.Subscriber('~test_report', String, self.__test_report_callback)

    def __test_report_callback(self, req):
        rospy.logdebug('report received')
        try:
            parsed_json = json.loads(req.data)
        except ValueError as e:
            rospy.logerr('Malformed json: ' + str(e))
            return
        parsed_json['date'] = datetime.now().isoformat()
        success = self.__cloud_api.test_report.send(parsed_json)
        rospy.logdebug('send result: ' + str(success))
        if not success:
            report_name = 'test_{}.json'.format(parsed_json['date'])
            report_path = '{}/{}'.format(self.__reports_path, report_name)
            report_handler = TestReport(report_path)
            report_handler.set_content(parsed_json)
            self.__add_report_db(
                'test_report', report_name, report_path
            )

    def __send_failed_test_reports(self):
        test_reports_response = self.__get_all_files_paths_db('test_report')
        if test_reports_response.status == CommandStatus.SUCCESS:
            for report in test_reports_response.filepaths:
                report_handler = TestReport(report.path)
                rospy.loginfo('Sending the test report of {}'.format(report_handler.content['date']))
                success = self.__cloud_api.test_report.send(report_handler.content)
                if success:
                    report_handler.delete()
                    self.__rm_report_db(report.id)
                else:
                    rospy.logerr('Unable to send the report')
