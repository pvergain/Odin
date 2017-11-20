import React from 'react';

import EditItem from './EditItem';

const ListItem = props => {
  const materialUrl = Urls['dashboard:education:included-material-detail']({
    material_id: props.material.id,
  });
  const materialEditUrl = Urls[
    'dashboard:education:course-management:edit-included-material'
  ]({
    course_id: props.course,
    material_id: props.material.id,
  });

  return (
    <div className="row">
      {window.props.isUserTeacher ? (
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
    const {materials, course} = this.props;

    return materials.length > 0 ? (
      <div className="list-group">
        {materials.map(material => {
          return (
            <ListItem material={material} course={course} key={material.id} />
          );
        })}
      </div>
    ) : (
      <div />
    );
  }
}

export default MaterialsList;
