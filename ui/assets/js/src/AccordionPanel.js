import React from 'react';
import MaterialsList from './MaterialsList';
import TasksList from './TasksList';
import SolvedRatio from './SolvedRatio';
import DropdownButton from './DropdownButton';
import EditItem from './EditItem';

const addMaterialMenuItems = (courseID, topicID) => {
  return [
    {
      value: 'From existing',
      url: Urls[
        'dashboard:education:course-management:add-included-material-from-existing'
      ]({
        course_id: courseID,
        topic_id: topicID,
      }),
    },
    {
      value: 'New',
      url: Urls[
        'dashboard:education:course-management:add-new-included-material'
      ]({
        course_id: courseID,
        topic_id: topicID,
      }),
    },
  ];
};

const addTaskMenuItems = (courseID, topicID) => {
  return [
    {
      value: 'From existing',
      url: Urls[
        'dashboard:education:course-management:add-included-task-from-existing'
      ]({
        course_id: courseID,
        topic_id: topicID,
      }),
    },
    {
      value: 'New',
      url: Urls['dashboard:education:course-management:add-new-included-task']({
        course_id: courseID,
      }),
    },
  ];
};

const AccordionPanel = props => {
  const collapseID = `collapse_${props.topic.id}`;
  const topicEditUrl = Urls[
    'dashboard:education:course-management:edit-topic'
  ]({
    course_id: props.topic.course,
    topic_id: props.topic.id,
  });

  return (
    <div className="panel panel-default">
      <div className="panel-heading">
        <h4 className="panel-title">
          <a
            className="accordion-toggle"
            data-toggle="collapse"
            data-parent="#accordion1"
            href={`#${collapseID}`}
            aria-expanded="true">
            <div className="row">
              <div className="col-md-3">
                Week {props.topic.week.number} - {props.topic.name}
              </div>
              {window.props.isUserTeacher ? (
                <div className="col-md-6">
                  <EditItem editUrl={topicEditUrl} size={1} />
                </div>
              ) : (
                <div className="col-md-6" />
              )}
              <div className="col-md-3">
                <SolvedRatio tasks={props.topic.tasks} />
              </div>
            </div>
          </a>
        </h4>
      </div>
      <div
        id={collapseID}
        className="panel-collapse collapse"
        aria-expanded="false">
        <div className="panel-body">
          <div className="col-md-4">
            <div className="mt-element-ribbon bg-grey-steel">
              <div className="ribbon ribbon-shadow ribbon-clip ribbon-color-success uppercase">
                <div className="ribbon-sub ribbon-clip" />Materials
              </div>
              <div className="ribbon-content">
                <MaterialsList
                  materials={props.topic.materials}
                  course={props.topic.course}
                />
                {window.props.isUserTeacher ? (
                  <DropdownButton
                    menuItems={addMaterialMenuItems(
                      props.topic.course,
                      props.topic.id,
                    )}>
                    Add Material
                  </DropdownButton>
                ) : (
                  ''
                )}
              </div>
            </div>
          </div>
          <div className="col-md-8">
            <div className="mt-element-ribbon bg-grey-steel">
              <div className="ribbon ribbon-shadow ribbon-clip ribbon-color-success uppercase">
                <div className="ribbon-sub ribbon-clip" />Tasks
              </div>
              <div className="ribbon-content">
                <TasksList
                  course={props.topic.course}
                  tasks={props.topic.tasks}
                />
                {window.props.isUserTeacher ? (
                  <DropdownButton
                    menuItems={addTaskMenuItems(
                      props.topic.course,
                      props.topic.id,
                    )}>
                    Add task
                  </DropdownButton>
                ) : (
                  ''
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AccordionPanel;
