import React from 'react';
import MaterialsList from './MaterialsList';
import TasksList from './TasksList';
import DropdownButton from './DropdownButton';
import {hasPassingSolutionForTask} from './SolutionUtils';

const addMaterialMenuItems = competitionSlug => {
  return [
    {
      value: 'From existing',
      url: Urls['competitions:create-competition-material-from-existing']({
        competition_slug: competitionSlug,
      }),
    },
    {
      value: 'New',
      url: Urls['competitions:create-new-competition-material']({
        competition_slug: competitionSlug,
      }),
    },
  ];
};

const addTaskMenuItems = competitionSlug => {
  return [
    {
      value: 'From existing',
      url: Urls['competitions:create-competition-task-from-existing']({
        competition_slug: competitionSlug,
      }),
    },
    {
      value: 'New',
      url: Urls['competitions:create-new-competition-task']({
        competition_slug: competitionSlug,
      }),
    },
  ];
};

const CompetitionAccordionPanel = props => {
  const collapseID = `collapse_${props.competition.id}`;
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
            {props.competition.name}
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
                  materials={props.competition.materials}
                  competition={props.competition}
                />
                {window.props.isUserJudgeInCompetition ? (
                  <DropdownButton
                    menuItems={addMaterialMenuItems(
                      props.competition.slug_url,
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
                  competition={props.competition}
                  tasks={props.competition.tasks}
                />
                {window.props.isUserJudgeInCompetition ? (
                  <DropdownButton
                    menuItems={addTaskMenuItems(props.competition.slug_url)}>
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

export default CompetitionAccordionPanel;
