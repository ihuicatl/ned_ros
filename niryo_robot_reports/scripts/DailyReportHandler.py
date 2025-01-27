import rospy
from StringIO import StringIO
from datetime import date, datetime

from niryo_robot_reports.DailyReport import DailyReport

# msg
from std_msgs.msg import Empty
from niryo_robot_msgs.msg import CommandStatus
from niryo_robot_status.msg import RobotStatus


class DailyReportHandler:
    def __init__(self, cloud_api, reports_path, add_report_db, rm_report_db, get_all_files_paths_db):
        self.__cloud_api = cloud_api
        self.__reports_path = reports_path
        self.__add_report_db = add_report_db
        self.__rm_report_db = rm_report_db
        self.__get_all_files_paths_db = get_all_files_paths_db
        self.__current_date = str(date.today())

        report_name = '{}.json'.format(self.__current_date)
        report_path = '{}/{}'.format(self.__reports_path, report_name)
        self.__daily_report = DailyReport(report_path)
        self.__daily_report.set_date(self.__current_date)
        add_report_response = self.__add_report_db(
            'daily_report', report_name, report_path
        )
        self.__current_id = add_report_response.message

        rospy.Subscriber('~new_day', Empty, self.__new_day_callback)
        rospy.Subscriber(
            '/niryo_robot_status/robot_status', RobotStatus,
            self.__robot_status_callback
        )
        self.__send_failed_daily_reports()

    def __new_day_callback(self, _req):
        current_day = str(date.today())
        if current_day == self.__current_date:
            return
        success = self.__cloud_api.daily_reports.send({
            'date':
            self.__current_date,
            'report':
            self.__daily_report.content
        })
        if success:
            self.__daily_report.delete()
            self.__rm_report_db(self.__current_id)
        self.__current_date = current_day
        new_path = '{}/{}.json'.format(self.__reports_path, self.__current_date)
        self.__daily_report.set_path(new_path)
        self.__daily_report.set_date(self.__current_date)

    def __robot_status_callback(self, req):
        if req.logs_status_str.lower() not in ['error', 'critical']:
            return
        log_io = StringIO(req.logs_message)
        level, from_node, msg, from_file, function, line = map(
            lambda x: x[x.index(':') + 2:], log_io.readlines()
        )
        formatted_log = '{} - {}: {} in {}.{}:{}'.format(
            level, from_node, msg, from_file, function, line
        )
        self.__daily_report.add_log(formatted_log, 'ROS', str(datetime.now()))

    def __send_failed_daily_reports(self):
        daily_reports_response = self.__get_all_files_paths_db('daily_report')
        if daily_reports_response.status == CommandStatus.SUCCESS:
            for report in daily_reports_response.filepaths:
                if report.date == self.__current_date:
                    continue
                report_handler = DailyReport(report.path)
                rospy.loginfo('Sending the report of {}'.format(report.date))
                success = self.__cloud_api.daily_reports.send(report_handler.content)
                if success:
                    report_handler.delete()
                    self.__rm_report_db(report.id)
                else:
                    rospy.logerr('Unable to send the report')
