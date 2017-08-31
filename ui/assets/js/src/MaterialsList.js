import React from 'react';

class MaterialsList extends React.Component {
  render() {
    const {materials} = this.props;

    // <a key={material.ObjectID} href={material.url} classNameName="list-group-item">
    //   material.name
    // </a>;

    return (
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
    );
  }
}

export default MaterialsList;
