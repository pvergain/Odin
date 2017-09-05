import React from "react";
import MaterialsList from "./MaterialsList";
import TasksList from "./TasksList";
import SolvedRatio from "./SolvedRatio";

const AccordionPanel = props => {
  const collapseID = `collapse_${props.topic.id}`;
  return (
    <div className="panel panel-default">
      <div className="panel-heading">
        <h4 className="panel-title">
          <a
            className="accordion-toggle"
            data-toggle="collapse"
            data-parent="#accordion1"
            href={`#${collapseID}`}
            aria-expanded="true"
          >
            {props.topic.name} <SolvedRatio tasks={props.topic.tasks} />
          </a>
        </h4>
      </div>
      <div
        id={collapseID}
        className="panel-collapse collapse"
        aria-expanded="false"
      >
        <div className="panel-body">
          <div className="col-md-4">
            <div className="mt-element-ribbon bg-grey-steel">
              <div className="ribbon ribbon-shadow ribbon-clip ribbon-color-success uppercase">
                <div className="ribbon-sub ribbon-clip" />Materials
              </div>
              <div className="ribbon-content">
                <MaterialsList materials={props.topic.materials} />
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
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AccordionPanel;
