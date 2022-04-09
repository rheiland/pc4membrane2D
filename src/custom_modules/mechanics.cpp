#include "./mechanics.h"

double circle_dist(double ptx, double pty)
{
    static double cx = 0.0;  // assume circle center is always at x=0
    static double R_circle = parameters.doubles("R_circle");

    double dx = ptx - cx;
    double dy = pty - R_circle;

    double d = sqrt(dx*dx + dy*dy) - R_circle;
    return d;
}

void epithelial_special_mechanics( Cell* pCell, Phenotype& phenotype, double dt )
{
	// Use this for homogenous attachment
	// BM adhesion 
		// is it time to detach (attachment lifetime)
		// am I unattached by capable? 
			// search through neighbors, find closest BM type agent 
			// form adhesion 
		// elastic adhesion 
	
	// plasto-elastic. 
		// elastic: movement towards rest position 
	
	// static int nRP = 0; // "rest_position"
	// std::vector<double> displacement = pCell->custom_data.vector_variables[nRP].value ; 
	
	custom_cell_update_mechanics( pCell , phenotype , dt );
	
	if( pCell->functions.add_cell_basement_membrane_interactions )
	{
		pCell->functions.add_cell_basement_membrane_interactions(pCell, phenotype,dt);
	}
	
	pCell->state.simple_pressure = 0.0; 
	
	//First check the neighbors in my current voxel
	std::vector<Cell*>::iterator neighbor;
	std::vector<Cell*>::iterator end = pCell->get_container()->agent_grid[pCell->get_current_mechanics_voxel_index()].end();
	for(neighbor = pCell->get_container()->agent_grid[pCell->get_current_mechanics_voxel_index()].begin(); neighbor != end; ++neighbor)
	{
		// pCell->add_potentials(*neighbor);
		// for each neighbor in current voxel, add it's contribution to displacement and velocity
		add_heterotypic_potentials( pCell, *neighbor ); 
		// add_spring_potentials(pCell, *neighbor );
	}
	std::vector<int>::iterator neighbor_voxel_index;
	std::vector<int>::iterator neighbor_voxel_index_end = 
		pCell->get_container()->underlying_mesh.moore_connected_voxel_indices[pCell->get_current_mechanics_voxel_index()].end();

	for( neighbor_voxel_index = 
		pCell->get_container()->underlying_mesh.moore_connected_voxel_indices[pCell->get_current_mechanics_voxel_index()].begin();
		neighbor_voxel_index != neighbor_voxel_index_end; 
		++neighbor_voxel_index )
		// search for neighboring voxels, if the cell is on a voxel phase and in contact with neighboring voxel subcell
	{
		if(!is_neighbor_voxel(pCell, pCell->get_container()->underlying_mesh.voxels[pCell->get_current_mechanics_voxel_index()].center, pCell->get_container()->underlying_mesh.voxels[*neighbor_voxel_index].center, *neighbor_voxel_index))
			continue;
		end = pCell->get_container()->agent_grid[*neighbor_voxel_index].end();
		for(neighbor = pCell->get_container()->agent_grid[*neighbor_voxel_index].begin();neighbor != end; ++neighbor)
		{
			// pCell->add_potentials(*neighbor);
			// for each cell in neigboring voxel, add it's contribution to displacement and velocity
			add_heterotypic_potentials( pCell, *neighbor ); 
			// add_spring_potentials(pCell, *neighbor );
		}
	}

	pCell->update_motility_vector(dt); 
	pCell->velocity += phenotype.motility.motility_vector; 
	return; 
}

// specialized potential function 
void add_heterotypic_potentials(Cell* my_cell , Cell* other_agent)
{
	static int nCellID = my_cell->custom_data.find_variable_index( "cell_ID" );   // cell blob ID (not subcell's)
	
	// if( this->ID == other_agent->ID )
	if( my_cell == other_agent )
	{ return; }
	
	static int subcell_repulsion_factor_index = my_cell->custom_data.find_variable_index("subcell_repulsion_factor");
	static int subcell_adhesion_factor_index = my_cell->custom_data.find_variable_index("subcell_adhesion_factor");

	double subcell_repulsion_factor = my_cell->custom_data[subcell_repulsion_factor_index];
	double subcell_adhesion_factor = my_cell->custom_data[subcell_adhesion_factor_index];
	
	static int nRAOC = my_cell->custom_data.find_variable_index( "relative_adhesion_other_cells" ); 
	static int nRAOCT = my_cell->custom_data.find_variable_index( "relative_adhesion_other_cell_types" ); 
	
	double rel_heterotypic_adhesion = my_cell->custom_data[nRAOCT];  
	double rel_other_cells_adhesion = my_cell->custom_data[nRAOC];  
	
	// 12 uniform neighbors at a close packing distance, after dividing out all constants
	static double simple_pressure_scale = 0.027288820670331; // 12 * (1 - sqrt(pi/(2*sqrt(3))))^2 
	// 9.820170012151277; // 12 * ( 1 - sqrt(2*pi/sqrt(3)))^2

	double distance = 0; 
	for( int i = 0 ; i < 3 ; i++ ) 
	{ 
		// find distance between cells 
		my_cell->displacement[i] = my_cell->position[i] - (*other_agent).position[i]; 
		distance += (my_cell->displacement[i]) * (my_cell->displacement[i]); 
	}
	// Make sure that the distance is not zero
	
	distance = std::max(sqrt(distance), 0.00001); 
	
	//Repulsive
	// Repulsion attributes
	// double R = my_cell->phenotype.geometry.radius + (*other_agent).phenotype.geometry.radius; 
	double R_sums = my_cell->phenotype.geometry.radius + (*other_agent).phenotype.geometry.radius; 
	
	// double RN = my_cell->phenotype.geometry.nuclear_radius + (*other_agent).phenotype.geometry.nuclear_radius;	
	// double R_nuclear_sums = my_cell->phenotype.geometry.nuclear_radius + (*other_agent).phenotype.geometry.nuclear_radius;	
	double temp_r, c;

	// if( distance > R ) 
	if( distance > R_sums ) 
	// R is basically distance between centers when they are attached, if distance is more, 
	// then there's still space between them
	{
		temp_r=0;
	}
	else
	{
		temp_r = -distance; // -d
		temp_r /= R_sums; // -d/R
		temp_r += 1.0; // 1-d/R
		temp_r *= temp_r; // (1-d/R)^2 
		
		// add the relative pressure contribution 
		my_cell->state.simple_pressure += ( temp_r / simple_pressure_scale ); // New July 2017 
	}
	
	// August 2017 - back to the original if both have same coefficient 
	double effective_repulsion = sqrt( my_cell->phenotype.mechanics.cell_cell_repulsion_strength * other_agent->phenotype.mechanics.cell_cell_repulsion_strength );
	temp_r *= effective_repulsion; 
	temp_r *= subcell_repulsion_factor;
	
	//////////////////////////////////////////////////////////////////
	
	// Adhesion
	double max_interactive_distance = my_cell->phenotype.mechanics.relative_maximum_adhesion_distance * my_cell->phenotype.geometry.radius + 
		(*other_agent).phenotype.mechanics.relative_maximum_adhesion_distance * (*other_agent).phenotype.geometry.radius;
		
	if(distance < max_interactive_distance ) 
	{	
		// double temp_a = 1 - distance/max_interactive_distance; 
		double temp_a = -distance; // -d
		temp_a /= max_interactive_distance; // -d/S
		temp_a += 1.0; // 1 - d/S 
		temp_a *= temp_a; // (1-d/S)^2 
		
		// August 2017 - back to the original if both have same coefficient 
		double effective_adhesion = sqrt( my_cell->phenotype.mechanics.cell_cell_adhesion_strength * other_agent->phenotype.mechanics.cell_cell_adhesion_strength ); 
		
		int my_id = (int) my_cell->custom_data[nCellID] ; 
		int other_id = (int) other_agent->custom_data[nCellID] ; 
	
		if( my_id != other_id )
		{ effective_adhesion *= rel_other_cells_adhesion; }
		
		if( my_cell->type != other_agent->type )
		{ effective_adhesion *= rel_heterotypic_adhesion; }
		temp_a *= effective_adhesion; 
		temp_a *= subcell_adhesion_factor;
		
		temp_r -= temp_a;
	}
	/////////////////////////////////////////////////////////////////
	if( fabs(temp_r) < 1e-16 )
	{ return; }
	temp_r /= distance;
	// multiply the temp_r value with velocity and add it to displacement, put it back in displacement
	axpy( &(my_cell->velocity) , temp_r , my_cell->displacement ); 
	
	return;
}

void heterotypic_update_cell_velocity( Cell* pCell, Phenotype& phenotype, double dt)
{
	if( pCell->functions.add_cell_basement_membrane_interactions )
	{
		pCell->functions.add_cell_basement_membrane_interactions(pCell, phenotype,dt);
	}
	
	pCell->state.simple_pressure = 0.0; 
	
	//First check the neighbors in my current voxel
	std::vector<Cell*>::iterator neighbor;
	std::vector<Cell*>::iterator end = pCell->get_container()->agent_grid[pCell->get_current_mechanics_voxel_index()].end();
	for(neighbor = pCell->get_container()->agent_grid[pCell->get_current_mechanics_voxel_index()].begin(); neighbor != end; ++neighbor)
	{
		// pCell->add_potentials(*neighbor);
		// for each neighbor in current voxel, add it's contribution to displacement and velocity
		add_heterotypic_potentials( pCell, *neighbor ); 
	}
	std::vector<int>::iterator neighbor_voxel_index;
	std::vector<int>::iterator neighbor_voxel_index_end = 
		pCell->get_container()->underlying_mesh.moore_connected_voxel_indices[pCell->get_current_mechanics_voxel_index()].end();

	for (neighbor_voxel_index = 
		pCell->get_container()->underlying_mesh.moore_connected_voxel_indices[pCell->get_current_mechanics_voxel_index()].begin();
		neighbor_voxel_index != neighbor_voxel_index_end; 
		++neighbor_voxel_index )

		// search for neighboring voxels, if the cell is on a voxel phase and in contact with neighboring voxel subcell
	{
		if (!is_neighbor_voxel(pCell, pCell->get_container()->underlying_mesh.voxels[pCell->get_current_mechanics_voxel_index()].center, pCell->get_container()->underlying_mesh.voxels[*neighbor_voxel_index].center, *neighbor_voxel_index))
			continue;
		end = pCell->get_container()->agent_grid[*neighbor_voxel_index].end();

		for (neighbor = pCell->get_container()->agent_grid[*neighbor_voxel_index].begin(); neighbor != end; ++neighbor)
		{
			// pCell->add_potentials(*neighbor);
			// for each cell in neigboring voxel, add it's contribution to displacement and velocity
			add_heterotypic_potentials( pCell, *neighbor ); 
		}
	}

	pCell->update_motility_vector(dt); 
	pCell->velocity += phenotype.motility.motility_vector; 
	return; 
}

void BM_special_mechanics( Cell* pCell, Phenotype& phenotype, double dt )
{
	return; 
}

void custom_cell_update_mechanics( Cell* pCell , Phenotype& phenotype , double dt )
{
	static int membrane_repulsion_factor_index = pCell->custom_data.find_variable_index("membrane_repulsion_factor");
	static int membrane_adhesion_factor_index = pCell->custom_data.find_variable_index("membrane_adhesion_factor");
	static int rel_max_membrane_adhesion_dist_i = pCell->custom_data.find_variable_index("rel_max_membrane_adhesion_dist");

	static int spring_break_push_index = pCell->custom_data.find_variable_index("spring_break_push");

	double membrane_repulsion_factor = pCell->custom_data[membrane_repulsion_factor_index];
	double membrane_adhesion_factor = pCell->custom_data[membrane_adhesion_factor_index];
	double relative_maximum_membrane_adhesion_distance = pCell->custom_data[rel_max_membrane_adhesion_dist_i];

    static int attach_lifetime_i = pCell->custom_data.find_variable_index( "attach_lifetime" ); 
    static int attach_time_i = pCell->custom_data.find_variable_index( "attach_time" ); 
    static int attached_to_BM_i = pCell->custom_data.find_variable_index( "attached_to_BM" ); 

	static int xvec_i = pCell->custom_data.find_variable_index("xvec");
	static int yvec_i = pCell->custom_data.find_variable_index("yvec");
	static int membrane_adhesion_dist_i = pCell->custom_data.find_variable_index("membrane_adhesion_dist");

    double adhesion_radius = phenotype.geometry.radius * relative_maximum_membrane_adhesion_distance;
	pCell->custom_data[membrane_adhesion_dist_i] = adhesion_radius;

    int ncells_attached = 0;
	double temp_r;
	double temp_a;

	// double R = adhesion_radius / 2;
	double adhesion_radius_half  = adhesion_radius / 2.0;

	double signed_dist = circle_dist(pCell->position[0],pCell->position[1]);
    // if (pCell->ID < 5)
    //     std::cout << "~~~ pCell->ID, signed_dist = " << pCell->ID << ", " << signed_dist << std::endl;

	// double displacement = signed_dist;
	// double displacement = 1.0;

    static double R_circle = parameters.doubles("R_circle");  // = circle y-value
    static double circle_x = 0.0;
	double dx = pCell->position[0];
	double dy = pCell->position[1] - R_circle;
    double norm_denom = sqrt(dx*dx + dy*dy);
	dx /= norm_denom;
	dy /= norm_denom;
	if (norm_denom > R_circle)
	{
		dy = -dy;
		dx = -dx;
	}
//	std::cout << "------ t, dx, dy = " << PhysiCell_globals.current_time << ", " << dx << ", " << dy << std::endl;

	// rwh: save for plotting
	pCell->custom_data[xvec_i] = dx;
	pCell->custom_data[yvec_i] = dy;

	// double dx = nx - pCell->position[0];
	// double dy = ny - pCell->position[1];
	// double dx = 0.0;
	// double dy = -1.0;
	std::vector<double> normal = {dx, dy, 0};
	double dv = 0.01;
	//===================================
    //   attach
    //===================================

    // rwh: why??
	// if (PhysiCell_globals.current_time > 2)
	// {
	// 	phenotype.motility.is_motile = false;
	// }

	if  (pCell->custom_data[attached_to_BM_i] == 1.0 )
	{
        std::cout << "-----> attached to BM\n";
		// if (displacement < 0) 
		if (signed_dist < 0) 
		{	
            std::cout << "-- signed_dist < 0: " << signed_dist << std::endl;
			// temp_a = displacement; // d
			temp_a = signed_dist; // d
			temp_a /= adhesion_radius; // d/Ra
			temp_a += 1.0; // 1-d/Ra
			temp_a *= temp_a; // (1-d/Ra)^2 
			temp_a *= membrane_adhesion_factor;
            std::cout << "    temp_a = " << temp_a << std::endl;

            // if (displacement > -R ) // repulsion
			if (signed_dist > -adhesion_radius_half ) // repulsion
			{
				// temp_r = displacement;
				// temp_r /= R; // d/R
				temp_r = signed_dist;
				temp_r /= adhesion_radius_half; // d/R
				// temp_r += 1.0; // 1-d/R 
				temp_r *= temp_r; // (1-d/R)^2 
				temp_r *= membrane_repulsion_factor;
				temp_a -= temp_r;
                std::cout << "(signed_dist > -adhesion_radius_half)  temp_a = " << temp_a << std::endl;
			}
			axpy(&(pCell->velocity), temp_a , normal);
		}
		else 
		{
			// if crosses the barrier, then zoom it back inside
			pCell->custom_data[attached_to_BM_i] = 0.0;
			pCell->custom_data[attach_time_i] = 0.0;
			// dv *= 1000;
            std::cout << "-- crossed barrier: zoom back in: dv=" << dv << std::endl;
			axpy(&(pCell->velocity), dv , normal);
			return;
		}
	}
	if( pCell->custom_data[attached_to_BM_i] == 0.0 )  // not attached to BM
	{
        std::cout << "---> NOT attached to BM\n";
		std::cout << "signed_dist, -adhesion_radius(=c_rad*rel_max_memb_adhes) (" << signed_dist <<", " << -adhesion_radius << std::endl;
        // if (displacement <= 0.0 && displacement > -adhesion_radius )
		// if (displacement > -adhesion_radius )
		if (signed_dist > -adhesion_radius )
        {
            pCell->custom_data[attached_to_BM_i] = 1.0;   // attached to BM now
            pCell->custom_data[attach_time_i] = 0.0;   // reset its time of being attached

			// temp_r = displacement; // d
			temp_r = signed_dist; // d
			temp_r /= adhesion_radius; // d/R

			// temp_r += 1.0; // 1-d/R 
			temp_r = 1.0 - temp_r; // rwh:  1-d/R 
			temp_r *= temp_r; // (1-d/R)^2 
			temp_r *= membrane_adhesion_factor;
            std::cout << "   signed_dist > -adhesion_radius "  << std::endl<< std::endl;
			axpy(&(pCell->velocity), temp_r , normal);
			std::cout << "   velocity (x,y)= " << pCell->velocity[0] <<", " << pCell->velocity[1] <<  std::endl<< std::endl;
        }
	}
	if (pCell->custom_data[attached_to_BM_i] == 1.0 && pCell->custom_data[attach_time_i] > pCell->custom_data[attach_lifetime_i])
	{
		pCell->custom_data[attached_to_BM_i] = 0.0;
		pCell->custom_data[attach_time_i] = 0.0;

		// static int spring_break_push_index = pCell->custom_data.find_variable_index("spring_break_push");
		double spring_break_push = pCell->custom_data[spring_break_push_index];
		// due to spring linkage breaking, a push in opposite direction
        std::cout << "-- attached to BM and attach_time >attach_lifetime: spring_break_push= " << spring_break_push << std::endl;
		axpy(&(pCell->velocity), spring_break_push , normal);
		return;
	}
    
    pCell->custom_data[attach_time_i] += dt;
	return; 
}