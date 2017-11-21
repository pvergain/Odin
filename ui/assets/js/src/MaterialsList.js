import React from 'react';

import EditItem from './EditItem';

const ListItem = props => {
  let materialUrl = '#';
  let materialEditUrl = '#';
  if (props.course) {
    materialUrl = Urls['dashboard:education:included-material-detail']({
      course_id: props.course,
      material_id: props.material.id,
    });
    materialEditUrl = Urls[
      'dashboard:education:course-management:edit-included-material'
    ]({
      course_id: props.course,
      material_id: props.material.id,
    });
  } else if (props.competition) {
    materialUrl = Urls['competitions:competition-material-detail']({
      competition_slug: props.competition.slug_url,
      material_id: props.material.id,
    });
    materialEditUrl = Urls['competitions:edit-competition-material']({
      competition_slug: props.competition.slug_url,
      material_id: props.material.id,
    });
  }
  return (
    <div className="row">
      {window.props.isUserTeacher || window.props.isUserJudgeInCompetition ? (
        <div>
          <div className="col-md-1">
            <EditItem editUrl={materialEditUrl} size={2} />
          </div>
          <div className="col-md-11">
            <a href={materialUrl} className="list-group-item">
              {props.material.identifier}
            </a>
          </div>
        </div>
      ) : (
        <div className="col-md-12">
          <a href={materialUrl} className="list-group-item">
            {props.material.identifier}
          </a>
        </div>
      )}
    </div>
  );
};

class MaterialsList extends React.Component {
  render() {
    return this.props.materials.length > 0 ? (
      <div className="list-group">
        {this.props.materials.map(material => {
          return this.props.course ? (
            <ListItem
              material={material}
              course={this.props.course}
              key={material.id}
            />
          ) : (
            <ListItem
              material={material}
              competition={this.props.competition}
              key={material.id}
            />
          );
        })}
      </div>
    ) : (
      <div />
    );
  }
}

export default MaterialsList;
