import React from 'react';

const ListItem = props => {
  const materialUrl = Urls['dashboard:education:material-detail']({
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
      <div className="col-md-9">
        <a href={materialUrl} className="list-group-item">
          {props.material.identifier}
        </a>
      </div>
      <div className="col-md-3">
        <a href={materialEditUrl}>
          <i
            className="fa fa-pencil fa-2x"
            style={{marginTop: '10px', marginRight: '10px'}}
          />
        </a>
      </div>
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
