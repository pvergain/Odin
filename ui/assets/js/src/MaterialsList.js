import React from 'react';

class MaterialsList extends React.Component {
  render() {
    const {materials} = this.props;

    return materials.length > 0 ? (
      <div className="list-group">
        {materials.map(material => {
          return (
            <a
              href={material.url}
              key={material.ObjectID}
              className="list-group-item">
              {material.identifier}
            </a>
          );
        })}
      </div>
    ) : (
      <div />
    );
  }
}

export default MaterialsList;
